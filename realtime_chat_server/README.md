# Real-Time Chat Server

## Setup (Windows)

```
cd realtime_chat_server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Start Redis

```
redis-server
```

(Install Redis if needed: https://redis.io/docs/install/install-redis/install-redis-on-windows/)

## Run Server

```
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Test

- POST /api/rooms {"name": "general"} → room_id=1
- WS ws://localhost:8000/ws/1?token=testuser
- Send JSON: {"type": "message", "content": "hi"} or "typing_start"
- Online tracked via Redis TTL sets.

## API

- GET /api/rooms
- GET /api/rooms/{room_id}/messages?limit=20
