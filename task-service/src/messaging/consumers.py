import logging

from aio_pika import Message
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.messaging.connection import get_channel
from src.messaging import queues_names
from src.schemas.messaging import TasksCount
from src.utils.unit_of_work import UnitOfWork


log = logging.getLogger(__name__)


async def get_tasks_count():
    ch = await get_channel()
    async with ch:
        queue = await ch.declare_queue(queues_names.TASKS_COUNT)

        uow = UnitOfWork()

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                try:
                    async with message.process():
                        body = TasksCount.model_validate_json(message.body.decode())
                        async with uow:
                            data = await uow.task.get_tasks_count_for_user(body.data.user_id)
                            body.data.count_assigned_tasks, body.data.count_authored_tasks = data

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
