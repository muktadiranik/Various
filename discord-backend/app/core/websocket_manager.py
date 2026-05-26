# app/core/websocket_manager.py
import asyncio
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionInfo:
    """Store connection metadata"""
    
    def __init__(self, websocket: WebSocket, user_id: int, connected_at: datetime):
        self.websocket = websocket
        self.user_id = user_id
        self.connected_at = connected_at
        self.last_heartbeat = datetime.utcnow()
        self.guilds: Set[int] = set()
        self.channels: Set[int] = set()


class WebSocketManager:
    """Manage WebSocket connections and rooms"""
    
    def __init__(self):
        self.active_connections: Dict[str, ConnectionInfo] = {}
        self.user_connections: Dict[int, Set[str]] = {}
        self.guild_rooms: Dict[int, Set[str]] = {}
        self.channel_rooms: Dict[int, Set[str]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int) -> str:
        """Accept and store a new WebSocket connection"""
        await websocket.accept()
        
        connection_id = f"{user_id}_{datetime.utcnow().timestamp()}"
        
        async with self._lock:
            connection_info = ConnectionInfo(websocket, user_id, datetime.utcnow())
            self.active_connections[connection_id] = connection_info
            
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
        
        logger.info(f"User {user_id} connected: {connection_id}")
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        async with self._lock:
            if connection_id not in self.active_connections:
                return
            
            connection_info = self.active_connections[connection_id]
            user_id = connection_info.user_id
            
            # Remove from guild rooms
            for guild_id in connection_info.guilds:
                if guild_id in self.guild_rooms:
                    self.guild_rooms[guild_id].discard(connection_id)
                    if not self.guild_rooms[guild_id]:
                        del self.guild_rooms[guild_id]
            
            # Remove from channel rooms
            for channel_id in connection_info.channels:
                if channel_id in self.channel_rooms:
                    self.channel_rooms[channel_id].discard(connection_id)
                    if not self.channel_rooms[channel_id]:
                        del self.channel_rooms[channel_id]
            
            # Remove from user connections
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from active connections
            del self.active_connections[connection_id]
            
            try:
                await connection_info.websocket.close()
            except:
                pass
        
        logger.info(f"Connection {connection_id} disconnected")
    
    async def join_guild(self, connection_id: str, guild_id: int) -> bool:
        """Add connection to a guild room"""
        async with self._lock:
            if connection_id not in self.active_connections:
                return False
            
            connection_info = self.active_connections[connection_id]
            connection_info.guilds.add(guild_id)
            
            if guild_id not in self.guild_rooms:
                self.guild_rooms[guild_id] = set()
            self.guild_rooms[guild_id].add(connection_id)
        
        logger.debug(f"Connection {connection_id} joined guild {guild_id}")
        return True
    
    async def leave_guild(self, connection_id: str, guild_id: int) -> bool:
        """Remove connection from a guild room"""
        async with self._lock:
            if connection_id not in self.active_connections:
                return False
            
            connection_info = self.active_connections[connection_id]
            connection_info.guilds.discard(guild_id)
            
            if guild_id in self.guild_rooms:
                self.guild_rooms[guild_id].discard(connection_id)
                if not self.guild_rooms[guild_id]:
                    del self.guild_rooms[guild_id]
        
        logger.debug(f"Connection {connection_id} left guild {guild_id}")
        return True
    
    async def join_channel(self, connection_id: str, channel_id: int) -> bool:
        """Add connection to a channel room"""
        async with self._lock:
            if connection_id not in self.active_connections:
                return False
            
            connection_info = self.active_connections[connection_id]
            connection_info.channels.add(channel_id)
            
            if channel_id not in self.channel_rooms:
                self.channel_rooms[channel_id] = set()
            self.channel_rooms[channel_id].add(connection_id)
        
        logger.debug(f"Connection {connection_id} joined channel {channel_id}")
        return True
    
    async def leave_channel(self, connection_id: str, channel_id: int) -> bool:
        """Remove connection from a channel room"""
        async with self._lock:
            if connection_id not in self.active_connections:
                return False
            
            connection_info = self.active_connections[connection_id]
            connection_info.channels.discard(channel_id)
            
            if channel_id in self.channel_rooms:
                self.channel_rooms[channel_id].discard(connection_id)
                if not self.channel_rooms[channel_id]:
                    del self.channel_rooms[channel_id]
        
        logger.debug(f"Connection {connection_id} left channel {channel_id}")
        return True
    
    async def send_to_connection(self, connection_id: str, message: dict) -> bool:
        """Send a message to a specific connection"""
        if connection_id not in self.active_connections:
            return False
        
        connection_info = self.active_connections[connection_id]
        try:
            await connection_info.websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending to connection {connection_id}: {e}")
            await self.disconnect(connection_id)
            return False
    
    async def send_to_user(self, user_id: int, message: dict) -> int:
        """Send a message to all connections of a user"""
        if user_id not in self.user_connections:
            return 0
        
        sent_count = 0
        for connection_id in self.user_connections[user_id]:
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_to_guild(self, guild_id: int, message: dict, exclude_connection_id: Optional[str] = None) -> int:
        """Broadcast a message to all connections in a guild"""
        if guild_id not in self.guild_rooms:
            return 0
        
        sent_count = 0
        for connection_id in self.guild_rooms[guild_id]:
            if connection_id == exclude_connection_id:
                continue
            
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast_to_channel(self, channel_id: int, message: dict, exclude_connection_id: Optional[str] = None) -> int:
        """Broadcast a message to all connections in a channel"""
        if channel_id not in self.channel_rooms:
            return 0
        
        sent_count = 0
        for connection_id in self.channel_rooms[channel_id]:
            if connection_id == exclude_connection_id:
                continue
            
            if await self.send_to_connection(connection_id, message):
                sent_count += 1
        
        return sent_count
    
    async def update_heartbeat(self, connection_id: str):
        """Update last heartbeat time for a connection"""
        if connection_id in self.active_connections:
            self.active_connections[connection_id].last_heartbeat = datetime.utcnow()
    
    async def check_heartbeats(self, timeout_seconds: int = 60):
        """Check for stale connections and disconnect them"""
        now = datetime.utcnow()
        stale_connections = []
        
        async with self._lock:
            for connection_id, info in self.active_connections.items():
                if (now - info.last_heartbeat).total_seconds() > timeout_seconds:
                    stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            logger.warning(f"Disconnecting stale connection {connection_id}")
            await self.disconnect(connection_id)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of connections for a user"""
        return len(self.user_connections.get(user_id, set()))
    
    def get_guild_connection_count(self, guild_id: int) -> int:
        """Get number of connections in a guild"""
        return len(self.guild_rooms.get(guild_id, set()))
    
    def get_channel_connection_count(self, channel_id: int) -> int:
        """Get number of connections in a channel"""
        return len(self.channel_rooms.get(channel_id, set()))


# Singleton instance
websocket_manager = WebSocketManager()