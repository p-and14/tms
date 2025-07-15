from fastapi import APIRouter

from src.api.v1.routers.task import router as task_router


router = APIRouter()

router.include_router(task_router, prefix="/v1", tags=["tasks | v1"])
