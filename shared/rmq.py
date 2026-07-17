# shared/rmq.py
import aio_pika
from typing import Optional
from .config import settings

class RabbitMQClient:
    _connection: Optional[aio_pika.Connection] = None
    _channel: Optional[aio_pika.Channel] = None

    @classmethod
    async def get_connection(cls) -> aio_pika.Connection:
        if cls._connection is None or cls._connection.is_closed:
            cls._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        return cls._connection

    @classmethod
    async def get_channel(cls) -> aio_pika.Channel:
        if cls._channel is None or cls._channel.is_closed:
            connection = await cls.get_connection()
            cls._channel = await connection.channel()
        return cls._channel