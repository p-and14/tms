import asyncio
from copy import deepcopy

import pytest
import sqlalchemy
from httpx import AsyncClient, ASGITransport
from sqlalchemy import sql, Result
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine

from typing import Generator, AsyncGenerator

from src.config import settings
from src.models.base import Base
from src.main import app
from src.models.task import Task
from src.utils.unit_of_work import UnitOfWork

from tests.fixtures import FakeUnitOfWork
from tests.fixtures import db_mocks


@pytest.fixture(scope="session")
def event_loop(request: pytest.FixtureRequest) -> Generator[asyncio.AbstractEventLoop]:
    """Returns a new event_loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_db(event_loop) -> AsyncGenerator[None]:
    """Creates a test base for the duration of the tests."""
    assert settings.MODE == "TEST"

    sqlalchemy_database_url = (
        f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}'
        f'@{settings.DB_HOST}:{settings.DB_PORT}/'
    )
    nodb_engine = create_async_engine(
        sqlalchemy_database_url,
        echo=False,
        future=True,
    )
    db = AsyncSession(bind=nodb_engine)

    db_exists_query = sql.text(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{settings.DB_NAME}'")
    db_exists: Result = await db.execute(db_exists_query)
    db_exists = db_exists.fetchone() is not None
    autocommit_engine = nodb_engine.execution_options(isolation_level="AUTOCOMMIT")
    connection = await autocommit_engine.connect()
    if not db_exists:
        db_create_query = sql.text(f"CREATE DATABASE {settings.DB_NAME}")
        await connection.execute(db_create_query)

    yield

    db_drop_query = sql.text(f"DROP DATABASE IF EXISTS {settings.DB_NAME} WITH (FORCE)")
    await db.close()
    await connection.execute(db_drop_query)
    await connection.close()
    await nodb_engine.dispose()


@pytest.fixture(scope="session")
async def db_engine(create_test_db: None) -> AsyncGenerator[AsyncEngine, None]:
    """Returns the test Engine."""
    engine = create_async_engine(
        settings.DATABASE_URL_asyncpg,
        echo=False,
        future=True,
        pool_size=50,
        max_overflow=100,
    ).execution_options(compiled_cache=None)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="session", autouse=True)
async def setup_schemas(db_engine: AsyncEngine) -> None:
    """Creates schemas in the test database."""
    assert settings.MODE == "TEST"

    schemas = (
        "task_schema",
    )

    async with db_engine.connect() as conn:
        for schema in schemas:
            await conn.execute(sqlalchemy.schema.CreateSchema(schema, if_not_exists=True))
            await conn.commit()


@pytest.fixture(scope="session", autouse=True)
async def setup_db(db_engine: AsyncEngine, setup_schemas: None) -> None:
    """Creates tables in the test database and insert needs data."""
    assert settings.MODE == "TEST"

    async with db_engine.begin() as db_conn:
        await db_conn.run_sync(Base.metadata.drop_all)
        await db_conn.run_sync(Base.metadata.create_all)


@pytest.fixture
async def transaction_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Returns a connection to the database.
    Any changes made to the database will NOT be applied, only for the duration of the TestCase.
    """
    connection = await db_engine.connect()
    await connection.begin()
    session = AsyncSession(bind=connection)

    yield session

    await session.rollback()
    await connection.close()


@pytest.fixture
def tasks() -> tuple[dict]:
    return deepcopy(db_mocks.TASKS)


@pytest.fixture
def users() -> tuple[dict]:
    return deepcopy(db_mocks.USERS)


@pytest.fixture
def tasks_orm(tasks) -> list[Task]:
    res = []
    for task in tasks:
        # if task.get("participants"):
        #     task["participants"] = [User(**participant) for participant in task["participants"]]
        res.append(Task(**task))
    return res


@pytest.fixture
def empty_fake_uow() -> Generator[FakeUnitOfWork]:
    """Returns the test UnitOfWork for a particular test."""
    _fake_uow = FakeUnitOfWork()
    yield _fake_uow


@pytest.fixture
def fake_uow_with_data(tasks_orm) -> Generator[FakeUnitOfWork]:
    """Returns the test UnitOfWork with tasks."""
    _fake_uow = FakeUnitOfWork(tasks_orm)
    yield _fake_uow


@pytest.fixture
async def async_client(fake_uow_with_data: FakeUnitOfWork) -> AsyncGenerator[AsyncClient, None]:
    """Returns async test client."""
    app.dependency_overrides[UnitOfWork] = lambda: fake_uow_with_data
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
