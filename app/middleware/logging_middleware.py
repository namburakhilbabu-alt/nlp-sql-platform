import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())[:8]
        start = time.time()
        logger.info(f"[{req_id}] -> GET {request.url.path}")
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"[{req_id}] Unhandled exception: {e}")
            raise
        elapsed = int((time.time() - start) * 1000)
        logger.info(f"[{req_id}] <- {response.status_code} | {elapsed}ms")        
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time"] = f"{elapsed}ms"
        return response
