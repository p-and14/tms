import json
from typing import Any


class RedisSerializer:
    @staticmethod
    def serialize(data: Any) -> str:
        return json.dumps(data)

    @staticmethod
    def deserialize(data: str) -> Any:
        return json.loads(data)
