from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from src.api.v1.services.user import UserService
from src.schemas.user import CreateUserRequest, Token, CreateUserResponse
from src.utils import auth_jwt


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")


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
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    jwt_payload = {
        "sub": user.id.hex
    }
    token = auth_jwt.encode_jwt(jwt_payload)
    return Token(access_token=token, token_type="Bearer")


@router.get("/me", response_model=CreateUserResponse, status_code=status.HTTP_200_OK)
async def get_me(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends()
) -> CreateUserResponse:
    current_user = await user_service.get_current_user(token=token)
    return CreateUserResponse(payload=current_user)
