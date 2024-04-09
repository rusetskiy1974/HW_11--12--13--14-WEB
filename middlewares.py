from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super(CustomHeaderMiddleware, self).__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['Request-time'] = str(datetime.now())
        return response
