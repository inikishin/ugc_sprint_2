import logging

from fastapi import Request, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger('gunicorn.error')


class LoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        logger.info('Request to [%s] with Request-Id [%s] from [%s]',
                    request.url,
                    request.headers.get('X-Request-Id'),
                    request.client.host,
                    extra={
                        'request_id': request.headers.get('X-Request-Id'),
                        'user_ip': request.client.host,
                        'tag': 'ugc_api',
                    })

        response = await call_next(request)

        return response


