from abc import ABC, abstractmethod
from typing import Any, Never, TypeVar, Generic, Type, Sequence

from pydantic import UUID4
from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base


class AbstractRepository(ABC):
    """An abstract class implementing the CRUD operations for working with any database."""

    @abstractmethod
    async def add_one(self, *args: Any, **kwargs: Any) -> Never:
        """Add one to the repository"""
        raise NotImplementedError

    @abstractmethod
    async def add_one_and_get_obj(self, *args: Any, **kwargs: Any) -> Never:
        """Add one to the repository and get obj"""
        raise NotImplementedError

    @abstractmethod
    async def bulk_add(self, *args: Any, **kwargs: Any) -> Never:
        """Add many to the repository"""
        raise NotImplementedError

    @abstractmethod
    async def get_one_by_id_or_none(self, *args: Any, **kwargs: Any) -> Never:
        """Get one from the repository, if it exists"""
        raise NotImplementedError

    @abstractmethod
    async def get_all(self, *args: Any, **kwargs: Any) -> Never:
        """Get all from the repository"""
        raise NotImplementedError

    @abstractmethod
    async def update_one_by_id(self, *args: Any, **kwargs: Any) -> Never:
        """Update one from the repository"""
        raise NotImplementedError

    @abstractmethod
    async def delete_one_by_id(self, *args: Any, **kwargs: Any) -> Never:
        """Delete one from the repository"""
        raise NotImplementedError


M = TypeVar("M", bound=Base)


class SqlAlchemyRepository(AbstractRepository, Generic[M]):
    """Basic repository implementing basic CRUD functions with a basic table.
    The repository works using the SqlAlchemy library."""

    _model: Type[M]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_one(self, **kwargs: Any) -> None:
        query = insert(self._model).values(**kwargs)
        await self._session.execute(query)

    async def add_one_and_get_obj(self, **kwargs: Any) -> M:
        query = insert(self._model).values(**kwargs).returning(self._model)
        obj = await self._session.execute(query)
        return obj.scalar_one()

    async def bulk_add(self, values: Sequence[dict[str, Any]]) -> None:
        query = insert(self._model).values(values)
        await self._session.execute(query)

    async def get_one_by_id_or_none(self, obj_id: UUID4) -> M | None:
        query = (
            select(self._model)
            .filter(self._model.id == obj_id)
        )
        obj = await self._session.execute(query)
        return obj.scalar_one_or_none()

    async def get_all(self, *args: Any, **kwargs: Any) -> Sequence[M]:
        query = select(self._model)
        res = await self._session.execute(query)
        return res.scalars().all()

    async def update_one_by_id(self, obj_id: UUID4, **kwargs: Any) -> M | None:
        query = (
            update(self._model)
            .filter(self._model.id == obj_id)
            .values(**kwargs)
            .returning(self._model)
        )
        obj = await self._session.execute(query)
        return obj.scalar_one_or_none()

    async def delete_one_by_id(self, obj_id: UUID4) -> None:
        query = (
            delete(self._model)
            .filter(self._model.id == obj_id)
        )
        await self._session.execute(query)
