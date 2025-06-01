from typing import Annotated
from uuid import uuid4, UUID

from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import String


uuidpk = Annotated[UUID, mapped_column(primary_key=True, default=uuid4)]
str_100 = Annotated[str, mapped_column(String(100))]


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()
        
    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"
