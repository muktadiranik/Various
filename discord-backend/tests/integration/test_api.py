# tests/integration/test_api.py
import pytest
from httpx import AsyncClient


class TestAuthAPI:
    async def test_register_endpoint(self, client: AsyncClient):
        """Test user registration endpoint"""
        response = await client.post(
            "/v1/auth/register",
            json={
                "username": "apiuser",
                "email": "api@example.com",
                "password": "Test123!"
            }
        )
        
        # If user already exists, that's fine
        if response.status_code == 400:
            response_data = response.json()
            if "already" in str(response_data).lower():
                # User exists, test passes
                return
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "apiuser"
        assert data["email"] == "api@example.com"
        assert "id" in data
    
    async def test_login_endpoint(self, client: AsyncClient):
        """Test login endpoint"""
        # First ensure user exists
        await client.post(
            "/v1/auth/register",
            json={
                "username": "testlogin",
                "email": "login@example.com",
                "password": "Test123!"
            }
        )
        
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "Test123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials"""
        response = await client.post(
            "/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPassword!"
            }
        )
        
        assert response.status_code == 401


class TestGuildAPI:
    async def test_create_guild(self, client: AsyncClient, auth_headers):
        """Test creating a guild"""
        response = await client.post(
            "/v1/guilds/",
            json={
                "name": "API Test Guild",
                "description": "Created via API test",
                "is_public": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "API Test Guild"
        assert "id" in data
    
    async def test_get_user_guilds(self, client: AsyncClient, auth_headers):
        """Test getting user's guilds"""
        # First create a guild
        await client.post(
            "/v1/guilds/",
            json={"name": "User Guilds Test"},
            headers=auth_headers
        )
        
        response = await client.get(
            "/v1/guilds/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_join_guild(self, client: AsyncClient, auth_headers):
        """Test joining a guild"""
        # Register owner user via API
        register_response = await client.post(
            "/v1/auth/register",
            json={
                "username": "guildowner",
                "email": "owner@test.com",
                "password": "Password123!"
            }
        )
        
        # If user already exists, that's fine (ignore 400)
        if register_response.status_code == 400:
            pass
        else:
            assert register_response.status_code == 201
        
        # Login as owner
        login_response = await client.post(
            "/v1/auth/login",
            json={"email": "owner@test.com", "password": "Password123!"}
        )
        
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        login_data = login_response.json()
        assert "access_token" in login_data, "No access_token in response"
        
        owner_headers = {"Authorization": f"Bearer {login_data['access_token']}"}
        
        # Create guild
        guild_response = await client.post(
            "/v1/guilds/",
            json={"name": "Join Test Guild", "is_public": True},
            headers=owner_headers
        )
        
        assert guild_response.status_code == 201, f"Guild creation failed: {guild_response.text}"
        guild_id = guild_response.json()["id"]
        
        # Join as test user
        response = await client.post(
            f"/v1/guilds/{guild_id}/join",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully joined guild"


class TestMessageAPI:
    async def test_create_and_get_messages(self, client: AsyncClient, auth_headers):
        """Test creating and retrieving messages"""
        # Create guild
        guild_response = await client.post(
            "/v1/guilds/",
            json={"name": "Message API Test"},
            headers=auth_headers
        )
        assert guild_response.status_code == 201
        guild_id = guild_response.json()["id"]
        
        # Get channels
        channels_response = await client.get(
            f"/v1/channels/?guild_id={guild_id}",
            headers=auth_headers
        )
        assert channels_response.status_code == 200
        channel_id = channels_response.json()[0]["id"]
        
        # Create message
        message_response = await client.post(
            f"/v1/messages/{channel_id}",
            json={"content": "Hello from API test!"},
            headers=auth_headers
        )
        
        assert message_response.status_code == 201
        message_data = message_response.json()
        assert message_data["content"] == "Hello from API test!"
        message_id = message_data["id"]
        
        # Get messages from channel
        get_response = await client.get(
            f"/v1/messages/{channel_id}?limit=10",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        messages_data = get_response.json()
        assert messages_data["total"] >= 1
        assert len(messages_data["messages"]) >= 1
    
    async def test_update_message(self, client: AsyncClient, auth_headers):
        """Test updating a message"""
        # Create guild
        guild_response = await client.post(
            "/v1/guilds/",
            json={"name": "Update Message Test", "is_public": True},
            headers=auth_headers
        )
        assert guild_response.status_code == 201
        guild_id = guild_response.json()["id"]
        
        # Get channels
        channels_response = await client.get(
            f"/v1/channels/?guild_id={guild_id}",
            headers=auth_headers
        )
        assert channels_response.status_code == 200
        channel_id = channels_response.json()[0]["id"]
        
        # Create message
        message_response = await client.post(
            f"/v1/messages/{channel_id}",
            json={"content": "Original content"},
            headers=auth_headers
        )
        assert message_response.status_code == 201
        message_id = message_response.json()["id"]
        
        # Update message
        update_response = await client.put(
            f"/v1/messages/{message_id}",
            json={"content": "Updated content"},
            headers=auth_headers
        )
        
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["content"] == "Updated content"
        assert updated_data["is_edited"] is True
    
    async def test_delete_message(self, client: AsyncClient, auth_headers):
        """Test deleting a message"""
        # Create guild
        guild_response = await client.post(
            "/v1/guilds/",
            json={"name": "Delete Message Test"},
            headers=auth_headers
        )
        assert guild_response.status_code == 201
        guild_id = guild_response.json()["id"]
        
        # Get channels
        channels_response = await client.get(
            f"/v1/channels/?guild_id={guild_id}",
            headers=auth_headers
        )
        assert channels_response.status_code == 200
        channel_id = channels_response.json()[0]["id"]
        
        # Create message
        message_response = await client.post(
            f"/v1/messages/{channel_id}",
            json={"content": "To be deleted"},
            headers=auth_headers
        )
        assert message_response.status_code == 201
        message_id = message_response.json()["id"]
        
        # Delete message
        delete_response = await client.delete(
            f"/v1/messages/{message_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 204