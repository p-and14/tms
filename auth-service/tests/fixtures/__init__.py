from typing import Any, Sequence
from uuid import UUID, uuid4
from types import TracebackType

from src.api.v1.services.user import UserService

from src.models.user import User

from tests.fixtures import db_mocks

class FakeUserRepository:
    """Test class for overriding the standard TaskRepository."""

    def __init__(self, users: list[User] = None):
        self.users: list[User] = users or []

    def get_users(self) -> list[User]:
        return self.users

    async def get_one_by_id_or_none(self, obj_id: UUID) -> User | None:
        for user in self.users:
            if user.id == obj_id:
                return user
        return None

    async def get_user_by_email(self, email: str) -> User | None:
        for user in self.users:
            if user.email == email:
                return user
        return None

    async def add_one_and_get_obj(self, **kwargs: Any) -> User:
        user = User(**kwargs)
        self.users.append(user)
        return user


class FakeUnitOfWork:
    """Test class for overriding the standard UnitOfWork.
    Provides isolation using transactions at the level of a single TestCase.
    """

    def __init__(
        self,
        users: list[User] = None,
    ) -> None:
        self.is_open: bool = False
        self.user = FakeUserRepository(users)

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass

    def get_users(self) -> list[User]:
        return self.user.get_users()


class FakeUserService(UserService):
    """Test class for overriding the standard TaskService."""
    def __init__(self, uow: FakeUnitOfWork) -> None:
        super().__init__()
        self.uow = uow
