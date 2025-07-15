from aio_pika import connect_robust
from aio_pika.abc import AbstractConnection, AbstractChannel

from src.config import settings

_rabbit_connection = None


async def get_connection() -> AbstractConnection:
    global _rabbit_connection
    if _rabbit_connection is None:
        _rabbit_connection = await connect_robust(settings.rabbit_settings.RABBIT_URL)
    return _rabbit_connection


async def get_channel() -> AbstractChannel:
    conn = await get_connection()
    return await conn.channel()
