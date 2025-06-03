import json
from typing import Any
from uuid import uuid4, UUID

from src.repositories.redis_repository import redis_user_repository, RedisUserRepository
from src.repositories.serializers import RedisSerializer


users = {
    uuid4() :{"name": "Иванов Иван Иванович"},
    uuid4(): bytes("Петров Петр Петрович", encoding="utf-8"),
    uuid4(): "Сидоров Сидр Сидорович"
}


def warning_case(user_repository: RedisUserRepository) -> None:
    unserialized_key = (123, {1: "1", "2": "gdfgdg"})
    user_repository.get_user(unserialized_key)
    user_repository.delete_user(unserialized_key)


def success_case(user_repository: RedisUserRepository, users: dict[UUID, Any]) -> None:
    for key, user in users.items():
        if not isinstance(user, (str, bytes)):
            user = RedisSerializer.serialize(user)

        user_repository.set_user(key, user)
        r_user = user_repository.get_user(key)
        try:
            r_user = RedisSerializer.deserialize(r_user)
        except json.decoder.JSONDecodeError:
            pass
        print(f"{key}: {r_user}")
        user_repository.delete_user(key)



if __name__ == "__main__":
    warning_case(redis_user_repository)
    success_case(redis_user_repository, users)
