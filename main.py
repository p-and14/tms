import json
from uuid import uuid4

from src.repositories.redis_repository import user_repository
from src.repositories.serializers import RedisSerializer


users = {
    uuid4() :{"name": "Иванов Иван Иванович"},
    uuid4(): bytes("Петров Петр Петрович", encoding="utf-8"),
    uuid4(): "Сидоров Сидр Сидорович"
}


for key, user in users.items():
    if not isinstance(user, (str, bytes)):
        user = RedisSerializer.serialize(user)

    print(f"{user_repository.set_user(key, user)=}")
    r_user = user_repository.get_user(key)
    try:
        r_user = RedisSerializer.deserialize(r_user)
    except json.decoder.JSONDecodeError:
        pass
    print(f"{r_user=}")
    print(f"{user_repository.delete_user(key)=}")
