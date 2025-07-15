from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from src.api.v1.services.user import UserService
from src.schemas.user import CreateUserRequest, Token, CreateUserResponse, UserWithTasksResponse

router = APIRouter(prefix="/users")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")


@router.post("/register", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user: CreateUserRequest,
    user_service: UserService = Depends()
) -> CreateUserResponse:
    created_user = await user_service.create_user(user)
    return CreateUserResponse(payload=created_user)


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends()
) -> Token:
    token = await user_service.get_jwt_token(form_data.username, form_data.password)
    return Token(access_token=token, token_type="Bearer")


@router.get("/info", response_model=UserWithTasksResponse, status_code=status.HTTP_200_OK)
async def get_info(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends()
) -> UserWithTasksResponse:
    user = await user_service.get_current_user_with_tasks_count(token=token)
    return UserWithTasksResponse(payload=user)
