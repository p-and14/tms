from pydantic import UUID4, BaseModel, Field, EmailStr


class UserID(BaseModel):
    id: UUID4


class UserDB(UserID):
    full_name: str = Field(max_length=100)
    email: EmailStr = Field()
