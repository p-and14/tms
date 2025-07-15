from typing import Any, Sequence
from uuid import UUID, uuid4
from types import TracebackType

from fastapi import HTTPException

from src.api.v1.services.task import TaskService

from src.models.task import Task, TaskParticipant, Status
from src.schemas.task import TaskFilters

from tests.fixtures import db_mocks
from tests.fixtures.db_mocks import USERS


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


class FakeUnitOfWork:
    """Test class for overriding the standard UnitOfWork.
    Provides isolation using transactions at the level of a single TestCase.
    """

    def __init__(
        self,
        tasks: list[Task] = None,
        participants: list[TaskParticipant] = None
    ) -> None:
        self.is_open: bool = False
        self.task = FakeTaskRepository(tasks, participants)

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


class FakeTaskService(TaskService):
    """Test class for overriding the standard TaskService."""
    def __init__(self, uow: FakeUnitOfWork) -> None:
        super().__init__()
        self.uow = uow

    @staticmethod
    async def check_user_existence(user_id: UUID, field_name: str) -> None:
        for user in USERS:
            if user["id"] == user_id:
                return
        raise HTTPException(422)


