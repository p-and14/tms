from datetime import datetime, date
import enum
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, text, Enum

from src.models.base import Base, uuid_pk, str_100


class Status(enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Role(enum.Enum):
    executor = "executor"
    watcher = "watcher"


class Task(Base):
    __tablename__ = "task"
    repr_cols_num = 4

    id: Mapped[uuid_pk]
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(Enum(Status, name="status", schema="task_schema"))
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        index=True)
    author_id: Mapped[UUID]
    assignee_id: Mapped[UUID | None]
    column_id: Mapped[UUID | None] = mapped_column(ForeignKey("task_schema.column.id", ondelete="SET NULL"))
    sprint_id: Mapped[UUID | None] = mapped_column(ForeignKey("task_schema.sprint.id", ondelete="SET NULL"))
    board_id: Mapped[UUID | None] = mapped_column(ForeignKey("task_schema.board.id", ondelete="SET NULL"))
    group_id: Mapped[UUID | None] = mapped_column(ForeignKey("task_schema.group.id", ondelete="SET NULL"))

    # participants: Mapped[list[UUID]] = relationship( # type: ignore  # noqa: F821
    #     back_populates="participant_tasks",
    #     # secondary="task_participant"
    # )
    column: Mapped["Column | None"] = relationship(back_populates="tasks")
    sprint: Mapped["Sprint | None"] = relationship(back_populates="tasks")
    board: Mapped["Board | None"] = relationship(back_populates="tasks")
    group: Mapped["Group | None"] = relationship(back_populates="tasks")

    def to_schema(self):
        from src.schemas.task import TaskDB
        return TaskDB(**self.__dict__)


class TaskParticipant(Base):
    __tablename__ = "task_participant"

    id: Mapped[uuid_pk]
    user_id: Mapped[UUID] = mapped_column(
        primary_key=True
    )
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_schema.task.id", ondelete="CASCADE"),
        primary_key=True
    )
    role: Mapped[Role] = mapped_column(Enum(Role, name="role", schema="task_schema"))
    # participant_tasks: Mapped[Task] = relationship()


class Board(Base):
    __tablename__ = "board"

    id: Mapped[uuid_pk]
    name: Mapped[str_100] = mapped_column(unique=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="board")
    columns: Mapped[list["Column"]] = relationship(back_populates="board")


class Column(Base):
    __tablename__ = "column"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100), unique=True)
    board_id: Mapped[UUID] = mapped_column(ForeignKey("task_schema.board.id", ondelete="CASCADE"))

    board: Mapped["Board"] = relationship(back_populates="columns")
    tasks: Mapped[list["Task"]] = relationship(back_populates="column")


class Sprint(Base):
    __tablename__ = "sprint"

    id: Mapped[uuid_pk]
    name: Mapped[str_100]
    start_date: Mapped[date]
    end_date: Mapped[date]

    tasks: Mapped[list["Task"]] = relationship(back_populates="sprint")


class Group(Base):
    __tablename__ = "group"

    id: Mapped[uuid_pk]
    name: Mapped[str_100]

    tasks: Mapped[list["Task"]] = relationship(back_populates="group")
