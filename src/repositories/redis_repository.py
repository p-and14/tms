import logging
from uuid import UUID

from redis import Redis

from src.core.redis_db import redis_client


log = logging.getLogger(__name__)


class RedisUserRepository:
    def __init__(self, client: Redis) -> None:
        self.client = client

    def set_user(self, user_id: UUID, full_name: str | bytes) -> bool:
        key = f"user:{user_id}"
        try:
            self.client.set(key, full_name) # type: ignore
            log.info(f"Пользователь c id={user_id} добавлен в redis")
        except Exception as e:
            log.error(f"Ошибка при добавлении пользователя c id={user_id}: {e}")
            return False
        return True
    
    def get_user(self, user_id: UUID) -> str | None:
        key = f"user:{user_id}"
        user = self.client.get(key)
        if user is None:
            log.warning(f"Не удалось получить пользователя c id={user_id}")
        return user  # type: ignore

    def delete_user(self, user_id: UUID) -> bool:
        key = f"user:{user_id}"
        try:
            res = self.client.delete(key)
            if res == 0:
                log.warning(f"Не удалось удалить пользователя c id={user_id}. Пользователь не найден")
            else:
                log.info(f"Пользователь c id={user_id} удалён из redis")
                return True
        except Exception as e:
            log.error(f"Ошибка при удалении пользователя c id={user_id}: {e}")
        return False


redis_user_repository = RedisUserRepository(redis_client)
