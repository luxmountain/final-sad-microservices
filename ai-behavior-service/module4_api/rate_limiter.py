"""
MODULE 4 — Rate Limiter (Redis-based hoặc in-memory)
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Rate limiter: 100 requests/phút/IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def setup_rate_limiter(app):
    """Gắn rate limiter vào FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
