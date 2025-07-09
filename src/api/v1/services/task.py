from fastapi import HTTPException, status
from pydantic import UUID4

from src.models.task import Task
from src.schemas.task import (
    CreateTaskRequest,
    TaskDB,
    TaskWithParticipants,
    UpdateTaskRequest,
    TaskFilters
)
from src.utils.constants import TASK_NOT_FOUND_MSG
from src.utils.service import BaseService, transaction_mode


class TaskService(BaseService):
    """Task service"""
    _repo: str = "task"

    @transaction_mode
    async def check_user_existence(self, user_id: UUID4, field_name: str) -> None:
        """Check if user exists"""
        if not await self.uow.user.get_one_by_id_or_none(user_id):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name.title()} with id {user_id} not found")

    @transaction_mode
    async def create_task(self, task: CreateTaskRequest, task_id: UUID4 = None) -> TaskDB:
        """Create a new task"""
        if task.author_id:
            await self.check_user_existence(task.author_id, "author")

        if task.assignee_id:
            await self.check_user_existence(task.assignee_id, "assignee")

        data = task.model_dump()
        if task_id:
            data["id"] = task_id
        created_task: Task = await self.uow.task.add_one_and_get_obj(**data)
        return created_task.to_schema()

    @transaction_mode
    async def get_task_with_participants(self, task_id: UUID4) -> TaskWithParticipants:
        """Get task with participants list"""
        task = await self.uow.task.get_task_with_participants(task_id=task_id)
        self.check_existence(task, detail=TASK_NOT_FOUND_MSG)
        return TaskWithParticipants(
            **task.to_schema().model_dump(),
            participants=[user.to_schema() for user in task.participants],
        )

    @transaction_mode
    async def get_tasks_by_filters(self, filters: TaskFilters) -> list[TaskDB]:
        """Get tasks by filters"""
        tasks = await self.uow.task.get_tasks_by_filters(filters)
        return [task.to_schema() for task in tasks]


    @transaction_mode
    async def partial_update_task(self, task_id: UUID4, task: UpdateTaskRequest) -> TaskDB:
        """Partial update a task by ID"""
        data = task.model_dump(exclude_unset=True)
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No request body specified")

        if task.author_id:
            await self.check_user_existence(task.author_id, "author")

        if task.assignee_id:
            await self.check_user_existence(task.assignee_id, "assignee")

        updated_task: Task = await self.uow.task.update_one_by_id(task_id=task_id, **data)
        self.check_existence(updated_task, detail=TASK_NOT_FOUND_MSG)
        return updated_task.to_schema()

    @transaction_mode
    async def delete_one_by_id(self, obj_id: UUID4) -> None:
        """Delete a task by ID"""
        task = await self.uow.task.get_one_by_id_or_none(obj_id=obj_id)
        self.check_existence(task, detail=TASK_NOT_FOUND_MSG)
        await self.uow.task.delete_task(task)
