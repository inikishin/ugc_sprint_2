import aiohttp

from http import HTTPStatus
from fastapi import Request, FastAPI
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, auth_url: str):
        super().__init__(app)
        self.auth_url = auth_url

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")

        if auth_header is None:
            return Response("Authorization header is missing", HTTPStatus.UNAUTHORIZED)

        async with aiohttp.ClientSession() as session:
            auth = await session.get(
                self.auth_url,
                headers={
                    "Authorization": auth_header,
                },
            )

            if auth.status == HTTPStatus.UNAUTHORIZED:
                return Response("Not authorized", HTTPStatus.UNAUTHORIZED)

        response = await call_next(request)

        return response
