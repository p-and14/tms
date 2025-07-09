from typing import Any, Sequence
from uuid import UUID, uuid4
from types import TracebackType

from src.api.v1.services.task import TaskService
from src.api.v1.services.user import UserService

from src.models.task import Task, TaskParticipant, Status
from src.models.user import User
from src.schemas.task import TaskFilters

from tests.fixtures import db_mocks


class FakeTaskRepository:
    """Test class for overriding the standard TaskRepository."""

    def __init__(self, tasks: list[Task] = None, participants: list[TaskParticipant] = None):
        self.tasks: list[Task] = tasks or []

    def get_tasks(self):
        return self.tasks

    async def get_one_by_id_or_none(self, obj_id: UUID) -> Task | None:
        for task in self.tasks:
            if task.id == obj_id:
                return task
        return None

    async def get_task_with_participants(self, task_id: UUID) -> Task | None:
        return await self.get_one_by_id_or_none(task_id)

    async def add_one_and_get_obj(self, **kwargs: Any) -> Task:
        if "id" not in kwargs:
            kwargs["id"] = uuid4()
        task = Task(**kwargs)
        self.tasks.append(task)
        return task

    async def get_tasks_by_filters(self, filters: TaskFilters) -> Sequence[Task]:
        has_filters = False
        res = []
        for task in self.tasks:
            add_task = None
            if filters.ids:
                has_filters = True
                if task.id not in filters.ids:
                    continue
                add_task = task
            if filters.status:
                has_filters = True
                if Status(task.status) not in filters.status:
                    continue
                add_task = task
            if filters.author_id:
                has_filters = True
                if task.author_id not in filters.author_id:
                    continue
                add_task = task
            if filters.assignee_id:
                has_filters = True
                if task.assignee_id not in filters.assignee_id:
                    continue
                add_task = task
            if filters.like:
                has_filters = True
                if filters.like not in task.title:
                    continue
                add_task = task
            if add_task:
                res.append(add_task)

        if not has_filters:
            res = self.tasks

        if filters.page is not None:
            return res[filters.offset:filters.limit]
        elif filters.per_page:
            return res[:filters.per_page]
        return res

    async def update_one_by_id(self, task_id: UUID, **kwargs: Any) -> Task | None:
        """Update a task by ID"""
        task = await self.get_one_by_id_or_none(task_id)
        if task is None:
            return None
        for k, v in kwargs.items():
            setattr(task, k, v)
        return task

    async def delete_task(self, task: Task) -> None:
        self.tasks.remove(task)


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
        tasks: list[Task] = None,
        users: list[User] = None,
        participants: list[TaskParticipant] = None
    ) -> None:
        self.is_open: bool = False
        self.task = FakeTaskRepository(tasks, participants)
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

    def get_tasks(self) -> list[Task]:
        return self.task.get_tasks()

    def get_users(self) -> list[User]:
        return self.user.get_users()


class FakeTaskService(TaskService):
    """Test class for overriding the standard TaskService."""
    def __init__(self, uow: FakeUnitOfWork) -> None:
        super().__init__()
        self.uow = uow


class FakeUserService(UserService):
    """Test class for overriding the standard TaskService."""
    def __init__(self, uow: FakeUnitOfWork) -> None:
        super().__init__()
        self.uow = uow
