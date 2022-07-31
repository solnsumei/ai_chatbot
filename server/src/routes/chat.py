import uuid
from http import HTTPStatus
from fastapi import APIRouter, Request, WebSocket, HTTPException, WebSocketDisconnect, Depends
from rejson import Path

from ..redis.config import RedisService
from ..redis.producer import Producer
from ..schema.chat import Chat
from ..socket.connection import ConnectionManager
from ..socket.utils import get_token

chat = APIRouter()

manager = ConnectionManager()
redis_service = RedisService()


# @route   POST /token
# @desc    Route to generate chat token
# @access  Public
@chat.post("/token")
async def token_generator(name: str, request: Request):
    if name is None or len(name.strip()) == 0:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail={
            "loc": "name", "msg": "Enter a valid name"
        })

    token = str(uuid.uuid4())

    # Create new chat session
    json_client = redis_service.create_rejson_connection()

    chat_session = Chat(
        token=token,
        messages=[],
        name=name
    )

    # Store chat session in redis JSON with the token as key
    json_client.jsonset(token, Path.rootPath(), chat_session.dict())

    # Set timeout for redis data
    redis_client = await redis_service.create_connection()
    await redis_client.expire(token, 3600)

    return chat_session.dict()


# @route   POST /refresh_token
# @desc    Route to refresh token
# @access  Public
@chat.post("refresh_token")
async def refresh_token(request: Request):
    return None


# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public
@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket = WebSocket, token: str = Depends(get_token)):
    await manager.connect(websocket)
    redis_client = await redis_service.create_connection()
    producer = Producer(redis_client)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            stream_data = {
                "token": data
            }
            await producer.add_to_stream(stream_data, "message_channel")
            await manager.send_personal_message(f"{data}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
