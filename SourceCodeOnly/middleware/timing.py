import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request processing time."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        request_id = getattr(request.state, "request_id", None)
        logger.info(
            f"Request processed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "process_time": process_time,
                "status_code": response.status_code,
                "request_id": request_id
            }
        )
        
        return response
