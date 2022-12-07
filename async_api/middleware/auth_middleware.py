from fastapi import Request, FastAPI
from fastapi.responses import Response
import requests
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, auth_url: str):
        super().__init__(app)
        self.auth_url = auth_url

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get('Authorization')

        if auth_header is None:
            return Response('Authorization header is missing', 401)

        auth = requests.get(self.auth_url,
                            headers={'Authorization': auth_header})
        print(auth.text)
        if auth.status_code == 401:
            return Response('Not authorized', 401)

        response = await call_next(request)

        return response


