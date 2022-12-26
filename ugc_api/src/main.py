import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import sentry_sdk
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
import uvicorn

from api.v1 import events
from core import config
from core.config import logger
from middleware.auth_middleware import AuthMiddleware
from middleware.logger_middleware import LoggerMiddleware

load_dotenv()

try:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_SDK_FAST_API'),
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        traces_sample_rate=1.0,
    )
except Exception as err:
    logger.error("Can't connect to sentry. Error: %s", err)

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(events.router, prefix='/api/v1/events', tags=['events'])

app.add_middleware(AuthMiddleware,
                   auth_url=os.getenv('AUTH_URL', 'http://localhost:5000/auth/who'))

app.add_middleware(LoggerMiddleware)


if __name__ == '__main__':
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
