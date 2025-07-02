from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, text

from src.models.base import Base, uuid_pk, str_100
from src.schemas.user import UserDB


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid_pk]
    full_name: Mapped[str_100]
    email: Mapped[str] = mapped_column(String(120), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())")
    )
    hashed_password: Mapped[str] = mapped_column(String(128))

    created_tasks: Mapped[list["Task"]] = relationship( # type: ignore  # noqa: F821
        back_populates="author",
        primaryjoin="User.id == Task.author_id"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship( # type: ignore  # noqa: F821
        back_populates="assignee",
        primaryjoin="User.id == Task.assignee_id"
        )
    participant_tasks: Mapped[list["Task"]] = relationship( # type: ignore  # noqa: F821
        back_populates="participants",
        secondary="task_participant"
    )

    def to_schema(self) -> UserDB:
        return UserDB(**self.__dict__)
