"""
Easeprompt In-Memory Rate Limiting Middleware.
Provides production-grade DDoS and bot abuse protection using a sliding-window algorithm.
Requires no external Redis or database setup.
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class InMemoryRateLimiter:
    """
    Sliding-window IP rate limiter.
    Tracks timestamps of recent requests per client IP.
    """
    def __init__(self, limit: int = 30, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        # Maps IP -> list of request timestamps
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.last_cleanup = time.time()

    def is_allowed(self, ip: str) -> Tuple[bool, int]:
        """
        Returns (is_allowed, retry_after_seconds).
        """
        now = time.time()
        self._periodic_cleanup(now)

        window_start = now - self.window_seconds
        # Filter timestamps within current window
        recent_timestamps = [t for t in self.requests[ip] if t > window_start]
        self.requests[ip] = recent_timestamps

        if len(recent_timestamps) >= self.limit:
            oldest_in_window = recent_timestamps[0]
            retry_after = max(1, int(oldest_in_window + self.window_seconds - now))
            return False, retry_after

        self.requests[ip].append(now)
        return True, 0

    def _periodic_cleanup(self, now: float):
        """Purge stale IPs every 5 minutes to avoid memory leaks."""
        if now - self.last_cleanup > 300:
            window_start = now - self.window_seconds
            stale_ips = [ip for ip, timestamps in self.requests.items() if not timestamps or timestamps[-1] < window_start]
            for ip in stale_ips:
                del self.requests[ip]
            self.last_cleanup = now


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware enforcing rate limits on sensitive API routes.
    """
    def __init__(self, app, limit: int = 30, window_seconds: int = 60):
        super().__init__(app)
        self.limiter = InMemoryRateLimiter(limit=limit, window_seconds=window_seconds)
        self.rate_limited_prefixes = ("/api/expand-stream", "/api/explain", "/api/test-prompt")

    def _get_client_ip(self, request: Request) -> str:
        """Extracts the genuine client IP even behind cloud load balancers / proxies."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Client IP is the first entry in comma-separated chain
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    async def dispatch(self, request: Request, call_next):
        # Only rate limit generation endpoints; static assets and health checks are exempt
        path = request.url.path
        if any(path.startswith(prefix) for prefix in self.rate_limited_prefixes):
            client_ip = self._get_client_ip(request)
            allowed, retry_after = self.limiter.is_allowed(client_ip)

            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please wait a moment before generating more prompts.",
                        "retry_after": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )

        return await call_next(request)
