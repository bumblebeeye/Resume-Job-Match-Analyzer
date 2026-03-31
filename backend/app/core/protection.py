from collections import defaultdict, deque
from typing import Deque
from threading import Lock
from time import monotonic

from fastapi import HTTPException, Request, status

from app.core.config import settings

_rate_limit_lock = Lock()
_rate_limit_history: dict[str, Deque[float]] = defaultdict(deque)


def enforce_api_protection(request: Request) -> None:
    _enforce_rate_limit(request)


def reset_rate_limit_history() -> None:
    with _rate_limit_lock:
        _rate_limit_history.clear()


def _enforce_rate_limit(request: Request) -> None:
    if request.method != "POST" or request.url.path != "/api/analyze":
        return

    window_seconds = max(settings.api_rate_limit_window_seconds, 1)
    max_requests = max(settings.api_rate_limit_requests, 1)
    client_key = f"{_get_client_identifier(request)}:{request.url.path}"
    now = monotonic()
    oldest_allowed_timestamp = now - window_seconds

    with _rate_limit_lock:
        request_times = _rate_limit_history[client_key]
        while request_times and request_times[0] <= oldest_allowed_timestamp:
            request_times.popleft()

        if len(request_times) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {window_seconds} seconds.",
            )

        request_times.append(now)


def _get_client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip() or "unknown"

    if request.client and request.client.host:
        return request.client.host

    return "unknown"
