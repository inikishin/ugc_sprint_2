import os
import redis

from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, request
from flask.logging import create_logger
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flasgger import APISpec, Swagger
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from auth.config.logging_cfg import file_handler, console_handler


app = Flask(__name__)

# opentelemetry
FlaskInstrumentor().instrument_app(app)

# logging
app.debug = True if os.getenv("DEBUG") else False
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
logger = create_logger(app)

# jwt
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 600)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 3000)
jwt = JWTManager(app)
jwt_redis_blocklist = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "test_redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD", "redis_secret"),
    db=2,
    decode_responses=True,
)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


ma = Marshmallow(app)

from auth.views import v1

app.register_blueprint(v1.authentication.bp)
app.register_blueprint(v1.roles.bp)
app.register_blueprint(v1.users.bp)
app.register_blueprint(v1.oauth.bp)

from auth import commands

app.register_blueprint(commands.bp)

from auth.views.schemas import (
    UserSchema,
    RoleSchema,
    UserLoginHistorySchema,
    RegisterInput,
)

spec = APISpec(
    title="Auth service",
    version="0.0.1",
    openapi_version="2.0",
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)
template = spec.to_flasgger(
    app,
    definitions=[UserSchema, RoleSchema, UserLoginHistorySchema, RegisterInput],
)
swagger = Swagger(app, template=template)


@app.before_request
def before_request():
    if os.getenv("env", "dev") == "prod":
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            raise RuntimeError("request id is required")


if __name__ == "__main__":
    app.run()
