import logging

from aio_pika import Message
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.messaging.connection import get_channel
from src.schemas.messaging import UserExists
from src.utils.unit_of_work import UnitOfWork
from src.messaging import queues_names

log = logging.getLogger(__name__)


async def check_user_existence():
    ch = await get_channel()
    async with ch:
        queue = await ch.declare_queue(queues_names.CHECK_EXISTENCE)

        uow = UnitOfWork()

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    async with message.process():
                        body = UserExists.model_validate_json(message.body.decode())
                        async with uow:
                            if await uow.user.get_one_by_id_or_none(body.data.user_id):
                                body.data.is_exists = True

                        await ch.default_exchange.publish(
                            Message(
                                body=body.model_dump_json().encode(),
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to
                        )
                except (ValidationError, SQLAlchemyError) as e:
                    log.error(f"Failed process message ({message.body.decode()}): {e}")
                    await message.nack(requeue=True)
