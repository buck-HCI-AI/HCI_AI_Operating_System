"""Redis cache service — get/set with JSON serialization and TTL."""
import json, redis as _redis
from typing import Any, Optional
from config import settings

_client: Optional[_redis.Redis] = None


def client() -> _redis.Redis:
    global _client
    if _client is None:
        _client = _redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True,
        )
    return _client


def get(key: str) -> Optional[Any]:
    raw = client().get(key)
    return json.loads(raw) if raw is not None else None


def set(key: str, value: Any, ttl: int = 300) -> None:
    client().setex(key, ttl, json.dumps(value, default=str))


def delete(key: str) -> None:
    client().delete(key)


def ping() -> bool:
    try:
        return client().ping()
    except Exception:
        return False
