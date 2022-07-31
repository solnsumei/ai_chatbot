from fastapi import WebSocket, status, Query
from typing import Optional

from ..redis.config import RedisService

redis_service = RedisService()


async def get_token(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    if token is None or len(token.strip()) == 0:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    redis_client = await redis_service.create_connection()
    is_exists = await redis_client.exists(token)

    if is_exists == 1:
        return token
    else:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Session not authenticated or expired token")
