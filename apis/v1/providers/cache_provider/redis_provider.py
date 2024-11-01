import redis
from typing import Any
from abc import ABC
from ...configs.redis_config import cache_db
from .base_provider import BaseCacheProvider  

class RedisCacheProvider(BaseCacheProvider, ABC):
    def __init__(self, expiration: int, redis_url: str):
        super().__init__(expiration)
        

    def get(self, key: str) -> Any | None:
        """
        Get value from Redis cache using the provided key.
        """
        value = cache_db.get(key)
        if value:
            return value.decode('utf-8')  # Assuming the value is stored as string
        return None

    def set(self, key: str, value: dict, ttl: int = None, merge: bool = None) -> None:
        """
        Set value in Redis cache with optional TTL and merge if value is a dict.
        """
        if ttl is None:
            ttl = self.expiration

        if merge and isinstance(value, dict):
            existing_value = self.get(key)
            if existing_value:
                existing_value.update(value)
                value = existing_value

        cache_db.setex(key, ttl, value)

    def delete(self, key: str) -> None:
        """
        Delete value from Redis cache using the provided key.
        """
        cache_db.delete(key)

    def gets(self, keys: list[str]) -> list[Any | None]:
        """
        Get multiple values from Redis cache using a list of keys.
        """
        return [self.get(key) for key in keys]

    def sets(self, data: dict, ttl: int = None) -> None:
        """
        Set multiple key-value pairs in Redis cache.
        """
        for key, value in data.items():
            self.set(key, value, ttl)

    def deletes(self, keys: list[str]) -> None:
        """
        Delete multiple keys from Redis cache.
        """
        cache_db.delete(*keys)

    def clear(self) -> None:
        """
        Clear all keys from Redis.
        """
        cache_db.flushdb()
