import datetime
import uuid

from fastapi import HTTPException, status
from jose import JWTError
from pydantic import EmailStr

from src.models.user import User
from src.schemas.user import CreateUserRequest, UserDB
from src.utils import auth_jwt
from src.utils.auth_jwt import hash_password, verify_password, decode_jwt
from src.utils.constants import USER_EXISTS_MSG
from src.utils.service import BaseService, transaction_mode


class UserService(BaseService):
    """User service"""
    _repo: str = "user"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    async def check_email_existence(self, email: EmailStr | str) -> None:
        """Check if email exists in database"""
        if await self.uow.user.get_user_by_email(email) is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=USER_EXISTS_MSG
            )

    @transaction_mode
    async def create_user(self, user: CreateUserRequest, user_id: uuid.UUID = None) -> UserDB:
        """Create new user"""
        await self.check_email_existence(user.email)
        hashed_password = hash_password(user.password)
        data = user.model_dump(exclude={"password"})
        if user_id:
            data["id"] = user_id

        created_user: User = await self.uow.user.add_one_and_get_obj(
            hashed_password=hashed_password.decode("utf-8"),
            **data
        )
        return created_user.to_schema()

    @transaction_mode
    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate user"""
        user = await self.uow.user.get_user_by_email(email)
        if not user:
            raise self.credentials_exception
        if not verify_password(password, user.hashed_password.encode("utf-8")):
            raise self.credentials_exception
        return user

    async def get_jwt_token(self, email: str, password: str) -> str:
        """Get JWT token"""
        user = await self.authenticate_user(email, password)
        jwt_payload = {"sub": user.id.hex}
        return auth_jwt.encode_jwt(jwt_payload)

    @transaction_mode
    async def get_current_user(self, token: str) -> UserDB:
        """Get current user from token"""
        try:
            payload = decode_jwt(token)
            user_id = payload.get("sub")
            if user_id is None:
                raise self.credentials_exception

            expire = payload.get("exp")
            now = datetime.datetime.now(tz=datetime.UTC).timestamp()
            if expire and expire < now:
                raise self.credentials_exception
        except JWTError:
            raise self.credentials_exception

        user = await self.uow.user.get_one_by_id_or_none(uuid.UUID(user_id))
        if user is None:
            raise self.credentials_exception
        return user.to_schema()
