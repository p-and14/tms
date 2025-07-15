from fastapi import APIRouter

from src.api.v1.routers.user import router as user_router


router = APIRouter()

router.include_router(user_router, prefix="/v1", tags=["users | v1"])
