from fastapi import Request
from slowapi import Limiter


def real_ip(request: Request) -> str:
    """First IP from X-Forwarded-For / X-Real-IP if set by a trusted reverse
    proxy in front of us, else the direct connecting address."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real = request.headers.get("x-real-ip")
    if real:
        return real
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=real_ip)
