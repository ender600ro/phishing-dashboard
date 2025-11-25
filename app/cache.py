# app/cache.py
import time
from typing import Any, Optional

_CACHE: dict[str, tuple[float, Any]] = {}
TTL_SECONDS = 60 * 60  # 1 hour

def get(key: str) -> Optional[Any]:
    now = time.time()
    hit = _CACHE.get(key)
    if not hit:
        return None
    ts, val = hit
    if now - ts > TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return val

def set(key: str, value: Any) -> None:
    _CACHE[key] = (time.time(), value)
