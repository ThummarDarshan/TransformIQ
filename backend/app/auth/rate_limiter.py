import time
from collections import defaultdict
from typing import Dict, List, Optional
from fastapi import Request, HTTPException, status
from app.config.settings import settings

class InMemoryRateLimiter:
    """
    Sliding-window in-memory rate limiter per IP address or user key.
    """
    def __init__(self):
        # Maps endpoint_name:client_identifier -> list of timestamps
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds
        
        # Clean older entries
        self.requests[key] = [t for t in self.requests[key] if t > window_start]
        
        if len(self.requests[key]) >= max_requests:
            return False
            
        self.requests[key].append(now)
        return True

    def reset(self):
        """Clears all stored rate limit history."""
        self.requests.clear()

limiter = InMemoryRateLimiter()

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def rate_limit(endpoint_name: str, max_per_minute: int):
    """
    FastAPI dependency for rate limiting by client IP.
    """
    async def dependency(request: Request):
        if not settings.RATE_LIMIT_ENABLED:
            return

        client_ip = get_client_ip(request)
        key = f"{endpoint_name}:{client_ip}"
        
        allowed = limiter.check_rate_limit(key, max_requests=max_per_minute, window_seconds=60)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Rate limit of {max_per_minute} requests/min reached for {endpoint_name}. Please retry after a brief pause.",
                headers={"Retry-After": "60"}
            )
    return dependency
