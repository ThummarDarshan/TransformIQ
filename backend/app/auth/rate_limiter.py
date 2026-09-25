import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, HTTPException, status
from app.config.settings import settings

class InMemoryRateLimiter:
    """
    Sliding-window in-memory rate limiter per IP address/client.
    """
    def __init__(self):
        # Maps endpoint_name:ip -> list of timestamps
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

limiter = InMemoryRateLimiter()

def rate_limit(endpoint_name: str, max_per_minute: int):
    """
    FastAPI dependency for rate limiting by client IP.
    """
    async def dependency(request: Request):
        if not settings.DEBUG and not settings.CHAT_RATE_LIMIT_ENABLED:
            return

        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"{endpoint_name}:{client_ip}"
        
        allowed = limiter.check_rate_limit(key, max_requests=max_per_minute, window_seconds=60)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {endpoint_name}. Maximum {max_per_minute} requests per minute allowed. Please wait a moment."
            )
    return dependency
