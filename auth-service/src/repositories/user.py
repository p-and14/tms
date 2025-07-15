from sqlalchemy import select

from src.models.user import User
from src.utils.repository import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository[User]):
    _model = User

    async def get_user_by_email(self, email: str) -> User | None:
        query = (
            select(self._model)
            .filter(self._model.email == email)
        )
        res = await self._session.execute(query)
        return res.scalar_one_or_none()
