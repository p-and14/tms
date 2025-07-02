from fastapi import APIRouter

from src.api.v1.routers.task import router as task_router
from src.api.v1.routers.user import router as user_router


router = APIRouter()
router.include_router(task_router, prefix="/v1", tags=["tasks | v1"])
router.include_router(user_router, prefix="/v1", tags=["users | v1"])
