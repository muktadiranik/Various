# Discord-like API

## Setup

```bash
cd discord_api
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Test

- POST /api/v1/auth/register {username, email, password}
- POST /api/v1/auth/login -> token
- POST /api/v1/servers {name} -> server
- GET /api/v1/servers
- POST /api/v1/channels {server_id, name, type}
- WS text: ws://localhost:8000/ws/text/{channel_id}?token=...
  Send JSON {'content': 'hello'} -> broadcast
- WS voice/video: ws://localhost:8000/ws/voice/{channel_id}?token=... send {'type': 'offer', 'sdp': '...', 'to_user_id': 2}

DB: discord.db auto-created.
JWT for auth.
WebRTC client needed for calls (getUserMedia/RTCPeerConnection).
