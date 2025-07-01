from datetime import datetime, date
import enum
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, text

from src.models.base import Base, uuidpk, str_100


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

    id: Mapped[uuidpk]
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[Status]
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        index=True)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    assignee_id: Mapped[UUID | None] = mapped_column(ForeignKey("user.id", ondelete="SET NULL"))
    column_id: Mapped[UUID | None] = mapped_column(ForeignKey("column.id", ondelete="SET NULL"))
    sprint_id: Mapped[UUID | None] = mapped_column(ForeignKey("sprint.id", ondelete="SET NULL"))
    board_id: Mapped[UUID | None] = mapped_column(ForeignKey("board.id", ondelete="SET NULL"))
    group_id: Mapped[UUID | None] = mapped_column(ForeignKey("group.id", ondelete="SET NULL"))

    author: Mapped["User"] = relationship( # type: ignore  # noqa: F821
        back_populates="created_tasks",
        primaryjoin="Task.author_id == User.id"
    )
    assignee: Mapped["User"] = relationship( # type: ignore  # noqa: F821
        back_populates="assigned_tasks",
        primaryjoin="Task.assignee_id == User.id"
    )
    participants: Mapped[list["User"]] = relationship( # type: ignore  # noqa: F821
        back_populates="participant_tasks",
        secondary="task_participant"
    )
    column: Mapped["Column | None"] = relationship(back_populates="tasks")
    sprint: Mapped["Sprint | None"] = relationship(back_populates="tasks")
    board: Mapped["Board | None"] = relationship(back_populates="tasks")
    group: Mapped["Group | None"] = relationship(back_populates="tasks")

    def to_schema(self):
        from src.schemas.task import TaskDB
        return TaskDB(**self.__dict__)


class TaskParticipant(Base):
    __tablename__ = "task_participant"

    id: Mapped[uuidpk]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True
    )
    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"),
        primary_key=True
    )
    role: Mapped[Role]


class Board(Base):
    __tablename__ = "board"

    id: Mapped[uuidpk]
    name: Mapped[str_100] = mapped_column(unique=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="board")
    columns: Mapped[list["Column"]] = relationship(back_populates="board")


class Column(Base):
    __tablename__ = "column"

    id: Mapped[uuidpk]
    name: Mapped[str] = mapped_column(String(100), unique=True)
    board_id: Mapped[UUID] = mapped_column(ForeignKey("board.id", ondelete="CASCADE"))

    board: Mapped["Board"] = relationship(back_populates="columns")
    tasks: Mapped[list["Task"]] = relationship(back_populates="column")


class Sprint(Base):
    __tablename__ = "sprint"

    id: Mapped[uuidpk]
    name: Mapped[str_100]
    start_date: Mapped[date]
    end_date: Mapped[date]

    tasks: Mapped[list["Task"]] = relationship(back_populates="sprint")


class Group(Base):
    __tablename__ = "group"

    id: Mapped[uuidpk]
    name: Mapped[str_100]
    
    tasks: Mapped[list["Task"]] = relationship(back_populates="group")
