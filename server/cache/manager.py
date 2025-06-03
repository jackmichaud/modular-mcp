from functools import lru_cache
from typing import Any
import time

cache_store = {}

def cached(ttl_seconds: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            if cache_key in cache_store:
                result, timestamp = cache_store[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            result = await func(*args, **kwargs)
            cache_store[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator