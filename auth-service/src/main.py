import asyncio
from contextlib import asynccontextmanager

import uvicorn
from  fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router
from src.messaging.connection import get_connection
from src.messaging.consumers import check_user_existence


@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbit_conn = await get_connection()
    task = asyncio.create_task(check_user_existence())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    await rabbit_conn.close()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
)
app.include_router(router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("src.main:app", reload=True)
