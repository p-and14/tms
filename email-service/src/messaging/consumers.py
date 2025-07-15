import logging

from src.messaging.connection import get_channel
from src.messaging import queues_names
from src.schemas.messaging import EmailNotification

log = logging.getLogger(__name__)

async def send_message() -> None:
    ch = await get_channel()
    async with ch:
        queue = await ch.declare_queue(queues_names.EMAIL_NOTIFICATIONS)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    async with message.process():
                        body = EmailNotification.model_validate_json(message.body.decode())
                        log.info(
                            f"Send email from {body.data.email_from} to {body.data.email_to}, "
                            f"subject: '{body.data.subject}', message: '{body.data.message}'"
                        )
                except Exception as e:
                    log.error(f"Failed process message ({message.body.decode()}): {e}")
                    await message.nack()
