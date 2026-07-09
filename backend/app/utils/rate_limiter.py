import time
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import threading
from app.utils.logging_config import logger

class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # Tokens per second
        self.tokens = float(capacity)
        self.last_update = time.time()
        self.lock = threading.Lock()

    def consume(self, amount: int = 1) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.last_update = now
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
            if self.tokens >= amount:
                self.tokens -= amount
                return True
            return False

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, capacity: int = 60, refill_rate: float = 1.0):
        super().__init__(app)
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Tuple[TokenBucket, float]] = {}  # IP/ID -> (Bucket, LastAccessedTime)
        self.lock = threading.Lock()
        
    def _get_bucket(self, key: str) -> TokenBucket:
        with self.lock:
            now = time.time()
            # Periodically clean stale buckets (idle for > 1 hour)
            if len(self.buckets) > 1000:
                self.buckets = {
                    k: v for k, v in self.buckets.items()
                    if now - v[1] < 3600
                }
                
            if key not in self.buckets:
                self.buckets[key] = (TokenBucket(self.capacity, self.refill_rate), now)
            else:
                self.buckets[key] = (self.buckets[key][0], now)
            return self.buckets[key][0]

    async def dispatch(self, request: Request, call_next):
        # Exclude documentation, CORS preflights, and health checks from rate limiting if needed
        if request.method == "OPTIONS" or request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)

        # Retrieve client IP or user ID (if available, e.g. from cookies)
        # For this middleware, we can check client host
        client_ip = request.client.host if request.client else "unknown"
        
        # We can also check if they have a cookie and key by token hash if preferred,
        # but client IP is a standard and robust default for raw endpoint protection.
        bucket = self._get_bucket(client_ip)
        
        if not bucket.consume(1):
            logger.warning("Rate limit exceeded", client_ip=client_ip, path=request.url.path)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Please try again later."}
            )

        return await call_next(request)
