import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from tests.utils import bulk_save_models


@pytest_asyncio.fixture
async def setup_tasks(setup_users: None, transaction_session: AsyncSession, tasks: tuple[dict]) -> None:
    """Creates tasks that will only exist within the session."""
    await bulk_save_models(transaction_session, Task, tasks)



