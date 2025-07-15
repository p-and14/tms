import functools
from abc import ABC, abstractmethod
from typing import Any, Never, Callable, TypeVar, Awaitable, Sequence

from fastapi import Depends, HTTPException, status
from pydantic import UUID4

from src.utils.repository import AbstractRepository
from src.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def transaction_mode(_func: T | None = None, *, auto_flush: bool = False) -> T | Callable[[T], T]:
    """Wraps the function in transaction mode.
    Checks if the UnitOfWork context manager is open.
    If not, then opens the context manager and opens a transaction.
    """
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(self: AbstractService, *args: Any, **kwargs: Any) -> T:
            if self.uow.is_open:
                res = await func(self, *args, **kwargs)
                if auto_flush:
                    await self.uow.flush()
                return res
            async with self.uow:
                return await func(self, *args, **kwargs)
        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)


class AbstractService(ABC):
    """Abstract service"""

    uow: AbstractUnitOfWork

    @abstractmethod
    async def add_one(self, *args: Any, **kwargs: Any) -> Never:
        """Add one entry"""
        raise NotImplementedError

    @abstractmethod
    async def add_one_and_get_obj(self, **kwargs: Any) -> Never:
        """Add one entry and get obj"""
        raise NotImplementedError

    @abstractmethod
    async def bulk_add(self, *args: Any, **kwargs: Any) -> Never:
        """Add many entries"""
        raise NotImplementedError

    @abstractmethod
    async def get_one_by_id_or_none(self, *args: Any, **kwargs: Any) -> Never:
        """Get one entry by its ID, if it exists"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, *args: Any, **kwargs: Any) -> Never:
        """Get all entries"""
        raise NotImplementedError

    @abstractmethod
    async def update_one_by_id(self, *args: Any, **kwargs: Any) -> Never:
        """Update a single entry by its ID"""
        raise NotImplementedError

    @abstractmethod
    async def delete_one_by_id(self, *args: Any, **kwargs: Any) -> Never:
        """Delete one entry by its ID"""
        raise NotImplementedError


class BaseService(AbstractService):
    """Base service"""

    _repo: str | None = None

    def __init__(self, uow: UnitOfWork = Depends()) -> None:
        self.uow = uow

        if not hasattr(self, "_repo") or self._repo is None:
            err_msg = f"Attribute '_repo' is required for class {self.__class__.__name__}"
            raise AttributeError(err_msg)

    @transaction_mode
    async def add_one(self, **kwargs: Any) -> None:
        await self._get_related_repo().add_one(**kwargs)

    async def add_one_and_get_obj(self, **kwargs: Any) -> Any:
        return  await self._get_related_repo().add_one_and_get_obj(**kwargs)

    @transaction_mode
    async def bulk_add(self, values: Sequence[dict[str, Any]]) -> None:
        await self._get_related_repo().bulk_add(values=values)

    @transaction_mode
    async def get_one_by_id_or_none(self, **kwargs: Any) -> Any:
        return  await self._get_related_repo().get_one_by_id_or_none(**kwargs)

    @transaction_mode
    async def get_all(self, **kwargs: Any) -> Sequence[Any]:
        return  await self._get_related_repo().get_all(**kwargs)

    @transaction_mode
    async def update_one_by_id(self, obj_id: UUID4, **kwargs: Any) -> Any:
        return  await self._get_related_repo().update_one_by_id(obj_id=obj_id, **kwargs)

    @transaction_mode
    async def delete_one_by_id(self, obj_id: UUID4) -> None:
        await self._get_related_repo().delete_one_by_id(obj_id=obj_id)

    @staticmethod
    def check_existence(obj: Any, detail: str) -> None:
        """Check if object exists"""
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

    def _get_related_repo(self) -> AbstractRepository:
        """Return the repository associated with the service."""
        return getattr(self.uow, self._repo)
