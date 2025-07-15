import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User
from tests.utils import bulk_save_models


@pytest_asyncio.fixture
async def setup_users(transaction_session: AsyncSession, users: tuple[dict]) -> None:
    """Creates users that will only exist within the session."""
    await bulk_save_models(transaction_session, User, users)
