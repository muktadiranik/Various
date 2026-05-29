#!/usr/bin/env python3
"""
Database seeding script using API endpoints
This script creates test data including users, guilds, channels, and messages
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import random
import string
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/v1"

# Test data
USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "Password123!"},
    {"username": "bob", "email": "bob@example.com", "password": "Password123!"},
    {"username": "charlie", "email": "charlie@example.com", "password": "Password123!"},
    {"username": "diana", "email": "diana@example.com", "password": "Password123!"},
    {"username": "eve", "email": "eve@example.com", "password": "Password123!"},
]

MESSAGES = [
    "Hello everyone! 👋",
    "Welcome to the server!",
    "Has anyone seen the new updates?",
    "I'm having a great day! 😊",
    "Does anyone need help with something?",
    "Check out this awesome feature!",
    "What's everyone working on?",
    "Great to see so many people online!",
    "Any plans for the weekend?",
    "I just finished a cool project!",
    "This is amazing! 🚀",
    "Can someone help me with this?",
    "Thanks for the support!",
    "Let's collaborate on something!",
    "Exciting news everyone!",
]

EMOJIS = ["👍", "❤️", "😂", "🎉", "🔥", "👏", "😮", "💯"]


class DatabaseSeeder:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.tokens: Dict[str, str] = {}
        self.users: Dict[str, Dict] = {}
        self.guilds: List[Dict] = []
        self.channels: List[Dict] = []
        self.messages: List[Dict] = []

    async def close(self):
        await self.client.aclose()

    async def register_user(self, user_data: Dict[str, str]) -> Dict[str, Any]:
        """Register a new user"""
        response = await self.client.post(
            f"{API_PREFIX}/auth/register",
            json=user_data
        )
        if response.status_code == 400:
            # User might already exist, try to login
            login_response = await self.client.post(
                f"{API_PREFIX}/auth/login",
                json={"email": user_data["email"], "password": user_data["password"]}
            )
            if login_response.status_code == 200:
                return login_response.json()
        response.raise_for_status()
        return response.json()

    async def login_user(self, email: str, password: str) -> str:
        """Login user and get access token"""
        response = await self.client.post(
            f"{API_PREFIX}/auth/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]

    async def create_guild(self, token: str, guild_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new guild"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{API_PREFIX}/guilds/",
            json=guild_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def create_channel(self, token: str, guild_id: int, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new channel in a guild"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{API_PREFIX}/channels/?guild_id={guild_id}",
            json=channel_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def send_message(self, token: str, channel_id: int, content: str) -> Dict[str, Any]:
        """Send a message to a channel"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{API_PREFIX}/messages/{channel_id}",
            json={"content": content},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def add_reaction(self, token: str, message_id: int, emoji: str) -> Dict[str, Any]:
        """Add a reaction to a message"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{API_PREFIX}/messages/{message_id}/reactions",
            json={"emoji": emoji},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def join_guild(self, token: str, guild_id: int) -> Dict[str, Any]:
        """Join a guild"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{API_PREFIX}/guilds/{guild_id}/join",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def create_role(self, token: str, guild_id: int, role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a role in a guild"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{API_PREFIX}/roles/?guild_id={guild_id}",
            json=role_data,
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def assign_role(self, token: str, guild_id: int, user_id: int, role_id: int) -> Dict[str, Any]:
        """Assign a role to a user"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.post(
            f"{API_PREFIX}/roles/assign",
            json={"guild_id": guild_id, "user_id": user_id, "role_id": role_id},
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def get_guild(self, token: str, guild_id: int) -> Dict[str, Any]:
        """Get guild details"""
        headers = {"Authorization": f"Bearer {token}"}
        response = await self.client.get(
            f"{API_PREFIX}/guilds/{guild_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    async def get_user_id_from_token(self, token: str) -> Optional[int]:
        """Extract user ID from token by getting current user info"""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = await self.client.get(
                f"{API_PREFIX}/users/me",
                headers=headers
            )
            if response.status_code == 200:
                user_data = response.json()
                return user_data["id"]
        except:
            pass
        return None

    async def seed_users(self):
        """Create all test users"""
        print("\n📝 Creating users...")
        for user_data in USERS:
            try:
                user = await self.register_user(user_data)
                # If register returns user data directly (not token), handle differently
                if "access_token" in user:
                    self.tokens[user_data["username"]] = user["access_token"]
                    # Also need to get user info
                    user_info = await self.get_user_id_from_token(user["access_token"])
                    if user_info:
                        self.users[user_data["username"]] = {"id": user_info, **user_data}
                else:
                    # User was created via register
                    self.users[user_data["username"]] = user
                    # Login to get token
                    token = await self.login_user(user_data["email"], user_data["password"])
                    self.tokens[user_data["username"]] = token
                
                print(f"  ✅ Created user: {user_data['username']} ({self.users[user_data['username']]['id']})")
            except Exception as e:
                print(f"  ❌ Failed to create user {user_data['username']}: {e}")
        
        print(f"\n✅ Created {len(self.users)} users")

    async def seed_guilds(self):
        """Create test guilds"""
        print("\n🏰 Creating guilds...")
        
        # Create main guild with alice as owner
        alice_token = self.tokens.get("alice")
        if alice_token:
            guild_data = {
                "name": "Gaming Community",
                "description": "A community for gamers to connect and play together! 🎮",
                "is_public": True
            }
            try:
                guild = await self.create_guild(alice_token, guild_data)
                self.guilds.append(guild)
                print(f"  ✅ Created guild: {guild['name']} (ID: {guild['id']})")
            except Exception as e:
                print(f"  ❌ Failed to create guild: {e}")
            
            # Create second guild
            guild_data2 = {
                "name": "Tech Enthusiasts",
                "description": "Discussing latest tech trends and innovations 💻",
                "is_public": True
            }
            try:
                guild2 = await self.create_guild(alice_token, guild_data2)
                self.guilds.append(guild2)
                print(f"  ✅ Created guild: {guild2['name']} (ID: {guild2['id']})")
            except Exception as e:
                print(f"  ❌ Failed to create second guild: {e}")
        
        print(f"\n✅ Created {len(self.guilds)} guilds")

    async def seed_channels(self):
        """Create channels in guilds"""
        print("\n📢 Creating channels...")
        
        alice_token = self.tokens.get("alice")
        if not alice_token:
            print("  ❌ No admin token available")
            return
        
        for guild in self.guilds:
            # First, verify that alice is the owner
            try:
                guild_info = await self.get_guild(alice_token, guild["id"])
                print(f"  ℹ️  Guild '{guild['name']}' owner_id: {guild_info.get('owner_id')}")
            except Exception as e:
                print(f"  ⚠️  Could not verify guild ownership: {e}")
            
            # Text channels - skip 'general' as it's created by default
            text_channels = [
                {"name": "announcements", "type": "text", "topic": "Server announcements"},
                {"name": "off-topic", "type": "text", "topic": "Casual conversations"},
                {"name": "support", "type": "text", "topic": "Get help here"},
            ]
            
            for channel_data in text_channels:
                try:
                    channel = await self.create_channel(alice_token, guild["id"], channel_data)
                    self.channels.append(channel)
                    print(f"  ✅ Created text channel: #{channel['name']} in {guild['name']}")
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 400:
                        error_text = e.response.text
                        if "already exists" in error_text.lower():
                            print(f"  ⚠️  Channel '{channel_data['name']}' already exists in {guild['name']}")
                        else:
                            print(f"  ❌ Failed to create text channel '{channel_data['name']}': {error_text}")
                    elif e.response.status_code == 403:
                        print(f"  ⚠️  Permission denied for text channel '{channel_data['name']}' in {guild['name']}")
                    else:
                        print(f"  ❌ Failed to create text channel '{channel_data['name']}': {e}")
                except Exception as e:
                    print(f"  ❌ Failed to create text channel '{channel_data['name']}': {e}")
            
            # Voice channels - skip 'General Voice' as it's created by default
            voice_channels = [
                {"name": "Gaming Voice", "type": "voice", "bitrate": 96000, "user_limit": 20},
            ]
            
            for channel_data in voice_channels:
                try:
                    channel = await self.create_channel(alice_token, guild["id"], channel_data)
                    self.channels.append(channel)
                    print(f"  ✅ Created voice channel: 🔊 {channel['name']} in {guild['name']}")
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 400:
                        error_text = e.response.text
                        if "already exists" in error_text.lower():
                            print(f"  ⚠️  Voice channel '{channel_data['name']}' already exists in {guild['name']}")
                        else:
                            print(f"  ❌ Failed to create voice channel '{channel_data['name']}': {error_text}")
                    elif e.response.status_code == 403:
                        print(f"  ⚠️  Permission denied for voice channel '{channel_data['name']}' in {guild['name']}")
                    else:
                        print(f"  ❌ Failed to create voice channel '{channel_data['name']}': {e}")
                except Exception as e:
                    print(f"  ❌ Failed to create voice channel '{channel_data['name']}': {e}")
        
        print(f"\n✅ Created {len(self.channels)} channels")

    async def seed_roles(self):
        """Create roles in guilds"""
        print("\n👑 Creating roles...")
        
        alice_token = self.tokens.get("alice")
        if not alice_token:
            print("  ❌ No admin token available")
            return
        
        roles_data = [
            {"name": "Moderator", "permissions": 0, "position": 50, "is_mentionable": True, "is_hoisted": True},
            {"name": "Member", "permissions": 0, "position": 10, "is_mentionable": False, "is_hoisted": False},
            {"name": "VIP", "permissions": 0, "position": 30, "is_mentionable": True, "is_hoisted": True},
        ]
        
        for guild in self.guilds:
            for role_data in roles_data:
                try:
                    role = await self.create_role(alice_token, guild["id"], role_data)
                    print(f"  ✅ Created role: {role['name']} in {guild['name']}")
                    
                    # Assign moderator role to bob in first guild
                    if role["name"] == "Moderator" and guild == self.guilds[0]:
                        bob_user = self.users.get("bob")
                        if bob_user:
                            try:
                                await self.assign_role(alice_token, guild["id"], bob_user["id"], role["id"])
                                print(f"     📌 Assigned {role['name']} to bob")
                            except Exception as e:
                                print(f"     ⚠️  Could not assign role: {e}")
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403:
                        print(f"  ⚠️  Permission denied for role {role_data['name']} in {guild['name']}")
                    else:
                        print(f"  ❌ Failed to create role {role_data['name']} in {guild['name']}: {e}")
                except Exception as e:
                    print(f"  ❌ Failed to create role {role_data['name']} in {guild['name']}: {e}")

    async def seed_members(self):
        """Add members to guilds"""
        print("\n👥 Adding members to guilds...")
        
        for guild in self.guilds:
            for username, user in self.users.items():
                if username != "alice":  # alice is already owner
                    token = self.tokens.get(username)
                    if token:
                        try:
                            await self.join_guild(token, guild["id"])
                            print(f"  ✅ {username} joined {guild['name']}")
                        except Exception as e:
                            print(f"  ❌ Failed to add {username} to {guild['name']}: {e}")

    async def seed_messages(self):
        """Create messages in channels"""
        print("\n💬 Creating messages...")
        
        message_count = 0
        
        for channel in self.channels:
            if channel.get("type") == "text":
                users_list = list(self.users.keys())
                messages_in_channel = 0
                
                for i in range(20):  # 20 messages per text channel
                    username = random.choice(users_list)
                    token = self.tokens.get(username)
                    if token:
                        content = random.choice(MESSAGES)
                        try:
                            message = await self.send_message(token, channel["id"], content)
                            self.messages.append(message)
                            message_count += 1
                            messages_in_channel += 1
                        except Exception as e:
                            # Silently skip errors (some may be permission issues)
                            pass
                
                if messages_in_channel > 0:
                    print(f"  ✅ Created {messages_in_channel} messages in #{channel['name']}")
        
        print(f"\n✅ Created {message_count} total messages")

    async def seed_reactions(self):
        """Add reactions to messages"""
        print("\n😊 Adding reactions...")
        
        reaction_count = 0
        
        # Add reactions to random messages
        sample_size = min(30, len(self.messages))
        if sample_size > 0:
            for message in random.sample(self.messages, sample_size):
                num_reactions = random.randint(1, 3)
                users_list = list(self.users.keys())
                
                for _ in range(num_reactions):
                    username = random.choice(users_list)
                    token = self.tokens.get(username)
                    if token:
                        emoji = random.choice(EMOJIS)
                        try:
                            await self.add_reaction(token, message["id"], emoji)
                            reaction_count += 1
                        except Exception:
                            pass  # Reaction might already exist or permission denied
        
        print(f"✅ Added {reaction_count} reactions")

    async def display_summary(self):
        """Display seeding summary"""
        print("\n" + "="*60)
        print("📊 DATABASE SEEDING COMPLETE!")
        print("="*60)
        print(f"\n📈 Summary:")
        print(f"  • Users created: {len(self.users)}")
        print(f"  • Guilds created: {len(self.guilds)}")
        print(f"  • Channels created: {len(self.channels)}")
        print(f"  • Messages created: {len(self.messages)}")
        
        print(f"\n👤 Users:")
        for username, user in self.users.items():
            print(f"  • {username} (ID: {user['id']}) - Email: {user['email']}")
        
        print(f"\n🏰 Guilds:")
        for guild in self.guilds:
            print(f"  • {guild['name']} (ID: {guild['id']})")
            if guild.get('description'):
                print(f"    Description: {guild['description']}")
        
        print(f"\n📢 Channels:")
        for channel in self.channels[:10]:  # Show first 10
            channel_type = channel.get('type', 'text')
            print(f"  • #{channel['name']} (ID: {channel['id']}) - Type: {channel_type}")
        if len(self.channels) > 10:
            print(f"  ... and {len(self.channels) - 10} more channels")
        
        print(f"\n🔐 Authentication Tokens (first 50 chars):")
        for username, token in list(self.tokens.items())[:3]:
            print(f"  • {username}: {token[:50]}...")
        
        print("\n✅ You can now test the API using these credentials!")
        print("\n📝 Example API calls:")
        print(f"  • Login: curl -X POST {BASE_URL}{API_PREFIX}/auth/login -H 'Content-Type: application/json' -d '{{\"email\":\"alice@example.com\",\"password\":\"Password123!\"}}'")
        if self.guilds:
            print(f"  • Get guilds: curl -X GET {BASE_URL}{API_PREFIX}/guilds/ -H 'Authorization: Bearer YOUR_TOKEN'")
        if self.channels:
            print(f"  • Get messages: curl -X GET {BASE_URL}{API_PREFIX}/messages/{self.channels[0]['id']} -H 'Authorization: Bearer YOUR_TOKEN'")
        print("="*60)

    async def run(self):
        """Run all seeding operations"""
        print("\n" + "="*60)
        print("🚀 STARTING DATABASE SEEDER")
        print("="*60)
        print(f"API Endpoint: {BASE_URL}")
        
        try:
            # Check if server is running
            response = await self.client.get("/health")
            if response.status_code != 200:
                print("❌ Server is not running. Please start the server first.")
                print("   Run: uvicorn app.main:app --reload")
                return
            print("✅ Server is running")
            
            # Seed data in order
            await self.seed_users()
            await self.seed_guilds()
            await self.seed_channels()
            await self.seed_roles()
            await self.seed_members()
            await self.seed_messages()
            await self.seed_reactions()
            await self.display_summary()
            
        except httpx.ConnectError:
            print("\n❌ Cannot connect to the server!")
            print("   Please make sure the server is running on", BASE_URL)
            print("   Run: uvicorn app.main:app --reload")
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.close()


async def main():
    seeder = DatabaseSeeder()
    await seeder.run()


if __name__ == "__main__":
    asyncio.run(main())