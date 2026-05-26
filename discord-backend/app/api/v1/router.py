# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1 import auth, users, guilds, channels, messages, roles, websocket, presence

router = APIRouter(prefix="/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(guilds.router)
router.include_router(channels.router)
router.include_router(messages.router)
router.include_router(roles.router)
router.include_router(presence.router)
router.include_router(websocket.router)

__all__ = ["router"]