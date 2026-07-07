import json
import redis
from src.core.config import settings
from typing import Any, Optional

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    def set_cache(self, key: str, value: Any, ttl: int = 300) -> None:
        serialized_val = json.dumps(value)
        self.client.set(key, serialized_val, ex=ttl)

    def get_cache(self, key: str) -> Optional[Any]:
        val = self.client.get(key)
        if val:
            return json.loads(val)
        return None

# Singleton Instance
redis_client = RedisClient()
