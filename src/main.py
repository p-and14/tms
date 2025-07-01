import uvicorn
from  fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router

app = FastAPI()

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
