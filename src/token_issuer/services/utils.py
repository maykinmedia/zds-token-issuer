from functools import wraps

from django.core.cache import caches


def cache(key: str, duration: int, name='default'):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key
            if args:
                cache_key = f"{cache_key}:{args}"
            if kwargs:
                cache_key = f"{cache_key}:{kwargs}"

            _cache = caches[name]

            result = _cache.get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            _cache.set(cache_key, result, duration)
            return result

        return wrapper

    return decorator
