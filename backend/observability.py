import logging
import time
import uuid
from collections import defaultdict
from threading import Lock

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("netguardian")

_metrics_lock = Lock()
_request_totals = defaultdict(int)
_request_durations = defaultdict(float)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        route = request.url.path

        with _metrics_lock:
            _request_totals[route] += 1
            _request_durations[route] += elapsed

        response.headers["x-request-id"] = request_id
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "path": route,
                "method": request.method,
                "status_code": response.status_code,
                "duration_ms": round(elapsed * 1000, 2),
            },
        )
        return response


def get_metrics_snapshot() -> dict:
    with _metrics_lock:
        result = {}
        for route, total in _request_totals.items():
            total_duration = _request_durations[route]
            result[route] = {
                "requests": total,
                "avg_duration_ms": round((total_duration / total) * 1000, 2) if total else 0.0,
            }
        return result

