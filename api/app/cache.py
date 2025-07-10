import time
from typing import Optional, Dict, Tuple
from app.settings import settings

_cache: Dict[str, Tuple[str, float]] = {}

def _is_expired(expiry_timestamp: float) -> bool:
    return time.time() > expiry_timestamp

def get_link_from_cache(url: str, storefront: str = "us") -> Optional[str]:
    cache_key = f"link:{url}:storefront:{storefront}"
    if cache_key in _cache:
        value, expiry_timestamp = _cache[cache_key]
        if not _is_expired(expiry_timestamp):
            return value
        else:
            # Remove expired entry
            del _cache[cache_key]
    
    return None

def set_link_in_cache(source_url: str, converted_url: str, storefront: str = "us"):
    cache_key = f"link:{source_url}:storefront:{storefront}"
    expiry_timestamp = time.time() + settings.LINK_CACHE_TTL_SECONDS
    _cache[cache_key] = (converted_url, expiry_timestamp)

def get_cache_stats() -> Dict[str, int]:
    spotify_count = 0
    apple_count = 0
    for key, value in _cache.items():
        if "spotify.com" in key:
            spotify_count += 1
        elif "apple.com" in key:
            apple_count += 1
    
    return {
        "total_entries": len(_cache),
        "spotify_count": spotify_count,
        "apple_count": apple_count
    }