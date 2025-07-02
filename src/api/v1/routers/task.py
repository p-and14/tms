from fastapi import APIRouter, Depends, status
from pydantic import UUID4

from src.api.v1.services.task import TaskService
from src.schemas.task import (
    CreateTaskRequest,
    CreateTaskResponse,
    TaskResponse,
    TaskListResponse,
    UpdateTaskRequest,
    TaskFilters
)

router = APIRouter(prefix="/tasks")


@router.post("/", response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: CreateTaskRequest,
    task_service: TaskService = Depends()
) -> CreateTaskResponse:
    """Create a new task"""
    created_task = await task_service.create_task(task)
    return CreateTaskResponse(payload=created_task)


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: UUID4,
    task_service: TaskService = Depends()
) -> TaskResponse:
    """Get a task"""
    task = await task_service.get_task_with_participants(task_id)
    return TaskResponse(payload=task)


@router.get("/", response_model=TaskListResponse, status_code=status.HTTP_200_OK)
async def get_all_tasks(
    task_service: TaskService = Depends(),
    filters: TaskFilters = Depends()
) -> TaskListResponse:
    """Get all tasks"""
    tasks = await task_service.get_tasks_by_filters(filters)
    return TaskListResponse(payload=tasks)


@router.patch("/{task_id}", response_model=CreateTaskResponse, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: UUID4,
    task: UpdateTaskRequest,
    task_service: TaskService = Depends()
) -> CreateTaskResponse:
    """Update a task"""
    updated_task = await task_service.partial_update_task(task_id, task)
    return CreateTaskResponse(payload=updated_task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID4,
    task_service: TaskService = Depends()
) -> None:
    """Delete a task"""
    await task_service.delete_one_by_id(task_id)
