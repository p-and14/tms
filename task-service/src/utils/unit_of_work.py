from abc import ABC, abstractmethod
from types import TracebackType
from typing import Never, Type, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import async_session_factory
from src.repositories.task import TaskRepository
from src.schemas.response import BaseCreateResponse


class AbstractUnitOfWork(ABC):
    """Abstract base class for unit of work"""
    is_open: bool = False
    task: TaskRepository

    @abstractmethod
    def __init__(self) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
            self,
            exc_type: Type[BaseException] | None,
            exc_val: BaseCreateResponse | None,
            exc_tb: TracebackType | None
    ) -> Never:
        raise NotImplementedError

    @abstractmethod
    async def flush(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):
    """The class responsible for the atomicity of transactions."""

    __slots__ = (
        "_session",
        "is_open",
        "task",
    )

    def __init__(self) -> None:
        self.is_open = False

    async def __aenter__(self) -> None:
        self._session: AsyncSession = async_session_factory()
        self.task = TaskRepository(session=self._session)
        self.is_open = True

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseCreateResponse | None,
        exc_tb: TracebackType | None
    ) -> None:
        if not exc_type:
            await self._session.commit()
        else:
            await self.rollback()
        await self._session.close()
        self.is_open = False

    async def flush(self) -> None:
        await self._session.flush()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def session_add(self, obj: Any) -> None:
        self._session.add(obj)

    async def session_refresh(self, obj: Any) -> None:
        await self._session.refresh(obj)

    def __getattr__(self, item: str) -> None:
        err_msg = f"{self.__class__.__name__} object has no attribute '{item}'."
        if item in self.__slots__ and not self.is_open:
            err_msg += f" Attempting to access '{item}' with a closed UnitOfWork."
        raise AttributeError(err_msg)
