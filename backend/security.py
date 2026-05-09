import threading
import time
from collections import defaultdict, deque
from typing import Any

from fastapi import Header, HTTPException, Request, status

from backend.config import settings

_rate_lock = threading.Lock()
_request_windows: dict[str, deque[float]] = defaultdict(deque)


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key or x_api_key != settings.api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized request",
        )
    return x_api_key


def _request_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def enforce_rate_limit(request: Request) -> None:
    now = time.time()
    key = _request_key(request)
    limit = settings.rate_limit_requests
    window = settings.rate_limit_window_sec

    with _rate_lock:
        q = _request_windows[key]
        while q and q[0] <= now - window:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )
        q.append(now)


SENSITIVE_KEYS = {"token", "password", "secret", "api_key", "authorization"}


def sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if k.lower() in SENSITIVE_KEYS:
                out[k] = "***"
            elif k == "blackboard":
                continue
            else:
                out[k] = sanitize_payload(v)
        return out
    if isinstance(value, list):
        return [sanitize_payload(v) for v in value]
    return value

