# app/api/v1/websocket.py
from fastapi import WebSocket, WebSocketDisconnect, Query, APIRouter, Depends
from typing import Optional
import json
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.websocket_manager import websocket_manager
from app.dependencies import get_db, get_current_user_ws
from app.services.message_service import MessageService
from app.services.permission_service import PermissionService
from app.services.presence_service import presence_service
from app.repositories.message_repo import MessageRepository
from app.repositories.channel_repo import ChannelRepository
from app.repositories.user_repo import UserRepository
from app.repositories.member_repo import MemberRepository
from app.repositories.role_repo import RoleRepository
from app.core.permissions import Permission, PermissionCalculator
from app.schemas.message import MessageCreate
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])


class WebSocketAuth:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.permission_service = None

    async def _get_permission_service(self):
        if not self.permission_service:
            member_repo = MemberRepository(self.db)
            role_repo = RoleRepository(self.db)
            channel_repo = ChannelRepository(self.db)
            self.permission_service = PermissionService(
                self.db, member_repo, role_repo, channel_repo
            )
        return self.permission_service

    async def authenticate(self, token: str) -> Optional[dict]:
        return await get_current_user_ws(token, self.db)

    async def can_join_channel(self, user_id: int, channel_id: int) -> bool:
        permission_service = await self._get_permission_service()
        permissions = await permission_service.get_user_channel_permissions(user_id, channel_id)
        return PermissionCalculator.has_permission(permissions, Permission.VIEW_CHANNEL)

    async def can_send_message(self, user_id: int, channel_id: int) -> bool:
        permission_service = await self._get_permission_service()
        permissions = await permission_service.get_user_channel_permissions(user_id, channel_id)
        return PermissionCalculator.has_permission(permissions, Permission.SEND_MESSAGES)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    auth = WebSocketAuth(db)
    connection_id = None
    user = None

    try:
        user = await auth.authenticate(token)
        if not user:
            await websocket.close(code=1008, reason="Invalid token")
            return

        connection_id = await websocket_manager.connect(websocket, user["id"])

        message_repo = MessageRepository(db)
        channel_repo = ChannelRepository(db)
        user_repo = UserRepository(db)
        message_service = MessageService(db, message_repo, channel_repo, user_repo)

        member_repo = MemberRepository(db)
        user_guilds = await member_repo.get_user_guilds(user["id"])

        for guild_member in user_guilds:
            guild_id = guild_member.guild_id
            await presence_service.set_user_online(user["id"], guild_id, "online")
            await websocket_manager.broadcast_to_guild(
                guild_id,
                {
                    "type": "presence_update",
                    "user_id": user["id"],
                    "username": user["username"],
                    "status": "online",
                    "guild_id": guild_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        await websocket.send_json({
            "type": "authenticated",
            "data": {
                "connection_id": connection_id,
                "user_id": user["id"],
                "username": user["username"],
                "timestamp": datetime.utcnow().isoformat()
            }
        })

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=60.0)
                await websocket_manager.update_heartbeat(connection_id)
                message_type = data.get("type")

                if message_type == "heartbeat":
                    await websocket.send_json({"type": "heartbeat_ack", "timestamp": datetime.utcnow().isoformat()})

                elif message_type == "join_guild":
                    guild_id = data.get("guild_id")
                    if guild_id:
                        permission_service = await auth._get_permission_service()
                        is_member = await permission_service.check_guild_membership(user["id"], guild_id)
                        if is_member:
                            await websocket_manager.join_guild(connection_id, guild_id)
                            await websocket.send_json({"type": "guild_joined", "guild_id": guild_id})

                elif message_type == "join_channel":
                    channel_id = data.get("channel_id")
                    if channel_id and await auth.can_join_channel(user["id"], channel_id):
                        await websocket_manager.join_channel(connection_id, channel_id)
                        await websocket.send_json({"type": "channel_joined", "channel_id": channel_id})

                elif message_type == "leave_channel":
                    channel_id = data.get("channel_id")
                    if channel_id:
                        await websocket_manager.leave_channel(connection_id, channel_id)

                elif message_type == "send_message":
                    channel_id = data.get("channel_id")
                    content = data.get("content")
                    reply_to_id = data.get("reply_to_id")
                    if channel_id and content and await auth.can_send_message(user["id"], channel_id):
                        message_data = MessageCreate(content=content, reply_to_id=reply_to_id)
                        permission_service = await auth._get_permission_service()
                        user_permissions = await permission_service.get_user_channel_permissions(user["id"], channel_id)
                        message = await message_service.create_message(
                            channel_id, user["id"], message_data, user_permissions
                        )
                        await websocket_manager.broadcast_to_channel(
                            channel_id,
                            {"type": "new_message", "data": message.dict(), "channel_id": channel_id}
                        )
                        await websocket.send_json({"type": "message_sent", "status": "success"})

                elif message_type == "typing_start":
                    channel_id = data.get("channel_id")
                    guild_id = data.get("guild_id")
                    if channel_id and guild_id and await auth.can_send_message(user["id"], channel_id):
                        await presence_service.start_typing(user["id"], user["username"], channel_id, guild_id)

                elif message_type == "typing_stop":
                    channel_id = data.get("channel_id")
                    if channel_id:
                        await presence_service.stop_typing(user["id"], channel_id)

                elif message_type == "ping":
                    await websocket.send_json({"type": "pong"})

            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error: {e}")

    except WebSocketDisconnect:
        if user:
            member_repo = MemberRepository(db)
            user_guilds = await member_repo.get_user_guilds(user["id"])
            for guild_member in user_guilds:
                guild_id = guild_member.guild_id
                await presence_service.set_user_offline(user["id"], guild_id)
                await websocket_manager.broadcast_to_guild(
                    guild_id,
                    {"type": "presence_update", "user_id": user["id"], "status": "offline", "guild_id": guild_id}
                )
    finally:
        if connection_id:
            await websocket_manager.disconnect(connection_id)
        await db.close()