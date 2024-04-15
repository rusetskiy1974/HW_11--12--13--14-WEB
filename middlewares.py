from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the middleware by passing in an ASGI application to wrap.

        :param self: Represent the instance of the class
        :param app: ASGIApp: Pass the asgi application instance to the middleware
        :return: The superclass of the customheadermiddleware class
        :doc-author: SergiyRus1974
        """
        super(CustomHeaderMiddleware, self).__init__(app)

    async def dispatch(self, request: Request, call_next):
        """
        The dispatch function is the first function called when a request comes in.
        It's job is to take the request and return a response. It can do this by calling
        the next middleware in line, or it can handle the request itself.

        :param self: Access the class attributes
        :param request: Request: Access the request object
        :param call_next: Call the next middleware in the chain
        :return: A response object
        :doc-author: SergiyRus1974
        """
        response = await call_next(request)
        response.headers['Request-time'] = str(datetime.now())
        return response
