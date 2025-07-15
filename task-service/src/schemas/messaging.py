from uuid import UUID

from pydantic import BaseModel


class BaseMessage(BaseModel):
    type: str


class UserID(BaseModel):
    user_id: UUID


class TasksForUserData(UserID):
    count_authored_tasks: int = 0
    count_assigned_tasks: int = 0


class TasksCount(BaseMessage):
    type: str = "tasks_count"
    data: TasksForUserData


class UserExistsData(UserID):
    is_exists: bool = False


class UserExists(BaseMessage):
    type: str = "user_exists"
    data: UserExistsData