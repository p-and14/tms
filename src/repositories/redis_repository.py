from uuid import UUID

from redis import Redis

from src.core.redis_db import redis_client


class UserRepository:
    def __init__(self, client: Redis) -> None:
        self.client = client

    def set_user(self, user_id: UUID, full_name: str | bytes) -> bool:
        return self.client.set(f"user:{user_id}", full_name) # type: ignore
    
    def get_user(self, user_id: UUID) -> str:
        return self.client.get(f"user:{user_id}") # type: ignore

    def delete_user(self, user_id: UUID) -> int:
        return self.client.delete(f"user:{user_id}") # type: ignore


user_repository = UserRepository(redis_client)
