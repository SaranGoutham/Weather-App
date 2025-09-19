# backend/core/ratelimit_inmemory.py
from __future__ import annotations
import time, threading
from typing import Tuple
from fastapi import Request, HTTPException, status
from .config import settings

# (ip, bucket) -> count
_STORE: dict[Tuple[str, int], int] = {}
_LOCK = threading.Lock()

def _client_ip(request: Request) -> str:
    if settings.TRUST_PROXY:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def rate_limit_ip(
    request: Request,
    *,
    limit: int | None = None,
    window_seconds: int = 60,
) -> None:
    limit = limit or settings.RATE_LIMIT_PER_MINUTE
    ip = _client_ip(request)
    bucket = int(time.monotonic() // window_seconds)
    key = (ip, bucket)

    with _LOCK:
        count = _STORE.get(key, 0) + 1
        _STORE[key] = count

        # small cleanup to avoid growth on very long runs
        if count == 1 and len(_STORE) > 10000:
            cutoff = bucket - 2
            for k in list(_STORE.keys()):
                if k[1] < cutoff:
                    _STORE.pop(k, None)

    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: {limit}/{window_seconds}s (per IP)",
        )
