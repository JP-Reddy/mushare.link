import redis
from app.settings import settings
from typing import Optional

def get_redis_client():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )

redis_client = get_redis_client()

def get_link_from_cache(url: str) -> Optional[str]:
    """
    Retrieves a converted link from the Redis cache using a normalized URL.
    """
    return redis_client.get(f"link:{url}")

def set_link_in_cache(source_url: str, converted_url: str):
    """
    Stores a converted link in the Redis cache with a TTL.
    """
    redis_client.setex(
        f"link:{source_url}",
        settings.LINK_CACHE_TTL_SECONDS,
        converted_url
    ) 