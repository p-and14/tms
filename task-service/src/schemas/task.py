import re
from dataclasses import dataclass
from uuid import UUID

from fastapi import Query
from pydantic import UUID4, BaseModel, Field, field_validator

from src.models.task import Status
from src.schemas.filter import TypeFilter
from src.schemas.response import BaseCreateResponse, BaseResponse

FORBIDDEN_SYMBOLS = r"<>{}|"


class TaskID(BaseModel):
    id: UUID4 = Field()


class TaskRequest(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = Field(default=None)
    status: Status
    author_id: UUID4
    assignee_id: UUID4 | None = Field(default=None)
    column_id: UUID4 | None = Field(default=None)
    sprint_id: UUID4 | None = Field(default=None)
    board_id: UUID4 | None = Field(default=None)
    group_id: UUID4 | None = Field(default=None)


class CreateTaskRequest(TaskRequest):
    @field_validator("title")
    @classmethod
    def validate_title_min_length(cls, value: str) -> str:
        if len(value) < 3:
            raise ValueError("Task title must be at least 3 characters")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str | None:
        pattern = f"[{FORBIDDEN_SYMBOLS}]"
        if value and re.search(pattern, value):
            raise ValueError(f"The task description must not contain '{FORBIDDEN_SYMBOLS}'")
        return value


class UpdateTaskRequest(CreateTaskRequest):
    title: str | None = Field(max_length=255, default=None)
    status: Status | None = Field(default=None)
    author_id: UUID4 | None = Field(default=None)


class TaskDB(TaskID, TaskRequest):
    pass


class CreateTaskResponse(BaseCreateResponse):
    payload: TaskDB


class TaskResponse(BaseResponse):
    payload: TaskDB


class TaskListResponse(BaseResponse):
    payload: list[TaskDB]


@dataclass
class TaskFilters(TypeFilter):
    ids: list[UUID] | None = Query(None)
    status: list[Status] | None = Query(None)
    author_id: list[UUID] | None = Query(None)
    assignee_id: list[UUID] | None = Query(None)
