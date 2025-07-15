from typing import Any, Sequence

from pydantic import UUID4
from sqlalchemy import select, update, func, case

from src.models.task import Task
from src.schemas.task import TaskFilters
from src.utils.repository import SqlAlchemyRepository


class TaskRepository(SqlAlchemyRepository[Task]):
    _model = Task

    async def get_tasks_count_for_user(self, user_id: UUID4) -> tuple[Any, Any]:
        """Get assigned_count and authored_count by user_id"""
        query = select(
                func.count(case((self._model.assignee_id == user_id, 1))).label("assigned_count"),
                func.count(case((self._model.author_id == user_id, 1))).label("authored_count")
            )

        res = await self._session.execute(query)
        assigned_count, authored_count = res.one()
        return assigned_count, authored_count

    async def update_one_by_id(self, task_id: UUID4, **kwargs: Any) -> Task | None:
        """Update a task by ID"""
        query = (
            update(self._model)
            .filter(self._model.id == task_id)
            .values(**kwargs)
            .returning(self._model)
        )
        obj = await self._session.execute(query)
        return obj.scalar_one_or_none()

    async def delete_task(self, task: Task) -> None:
        """Delete a task"""
        await self._session.delete(task)

    async def get_tasks_by_filters(self, filters: TaskFilters) -> Sequence[Task]:
        """Get tasks by filters"""
        query = select(self._model)

        if filters.ids:
            query = query.filter(self._model.id.in_(filters.ids))

        if filters.status:
            query = query.filter(self._model.status.in_(filters.status))

        if filters.author_id:
            query = query.filter(self._model.author_id.in_(filters.author_id))

        if filters.assignee_id:
            query = query.filter(self._model.assignee_id.in_(filters.assignee_id))

        if filters.like:
            query = query.filter(self._model.title.like(f"%{filters.like}%"))

        if filters.page is not None:
            query = query.offset(filters.offset).limit(filters.limit)
        elif filters.per_page:
            query = query.limit(filters.per_page)

        res = await self._session.execute(query)
        return res.scalars().all()
