import re

from pydantic import UUID4, BaseModel, Field, EmailStr, field_validator

from src.schemas.response import BaseCreateResponse, BaseResponse


class Token(BaseModel):
    access_token: str
    token_type: str


class UserID(BaseModel):
    id: UUID4


class UserRequest(BaseModel):
    full_name: str = Field(max_length=100)
    email: EmailStr = Field(max_length=120)


class UserDB(UserID, UserRequest):
    pass


class UserWithTasksCount(UserDB):
    count_authored_tasks: int = Field(default=0)
    count_assigned_tasks: int = Field(default=0)


class CreateUserRequest(UserRequest):
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

class CreateUserResponse(BaseCreateResponse):
    payload: UserDB


class UserResponse(BaseResponse):
    payload: UserDB


class UserWithTasksResponse(BaseResponse):
    payload: UserWithTasksCount
