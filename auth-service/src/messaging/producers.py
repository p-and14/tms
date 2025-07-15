import asyncio
import logging
from uuid import UUID, uuid4

from aio_pika import Message
from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError, EmailStr

from src.messaging.connection import get_channel
from src.messaging import queues_names
from src.schemas.messaging import TasksForUserData, TasksCount, EmailNotification, EmailNotificationData

log = logging.getLogger(__name__)


async def get_tasks_count(user_id: UUID) -> TasksForUserData | None:
    ch = await get_channel()
    async with ch:
        queue = await ch.declare_queue(queues_names.TASKS_COUNT)

        payload = TasksCount(data=TasksForUserData(user_id=user_id)).model_dump_json()

        callback_queue = await ch.declare_queue(exclusive=True, auto_delete=True)
        correlation_id = str(uuid4())
        future = asyncio.get_event_loop().create_future()

        async def on_response(message: AbstractIncomingMessage) -> None:
            if message.correlation_id == correlation_id:
                try:
                    data = TasksCount.model_validate_json(message.body.decode())
                    future.set_result(data.data)
                except ValidationError as e:
                    log.error(f"Failed validate TasksCount({message.body.decode()}): {e}")

        await callback_queue.consume(on_response)

        await ch.default_exchange.publish(
            Message(
                body=payload.encode(),
                reply_to=callback_queue.name,
                correlation_id=correlation_id,
            ),
            routing_key=queue.name,
        )

        return await future


async def send_email_notification(email: EmailStr | str, subject: str, message: str) -> None:
    ch = await get_channel()
    async with ch:
        queue = await ch.declare_queue(queues_names.EMAIL_NOTIFICATIONS)

        payload = EmailNotification(data=EmailNotificationData(
            email_to=email, email_from="info@tms.com",
            message=message, subject=subject
        )).model_dump_json()

        await ch.default_exchange.publish(
            Message(
                body=payload.encode(),
            ),
            routing_key=queue.name,
        )
