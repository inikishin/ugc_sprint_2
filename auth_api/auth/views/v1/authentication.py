from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest

from auth.main import logger
from auth.models import db
from auth.services.authentication import AuthService
from auth.services.users import UserService
from auth.views.schemas import user_schema, login_input_schema,\
    register_input_schema
from auth.utils.api_error_handling_wrapper import api_error_handling_wrapper
from auth.utils.rbac import allow
from auth.utils.opentelemetry_tracer import trace
from auth.utils.rate_limits import limit_leaky_bucket

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/who', methods=['GET'])
@allow(['admin', 'user'])
@jwt_required()
@limit_leaky_bucket
def who():
    """Точка возвращает информацию залогинен ли пользователь
    ---
    description: Точка возвращает информацию залогинен ли пользователь
    definitions:
      WhoOutputData:
        type: object
        properties:
          auth:
            type: boolean
          user:
            type: object
            properties:
              email:
                type: string
              first_name:
                type: string
              last_name:
                type: string
              sub:
                type: string
              role_names:
                type: array
                items:
                  type: string
    responses:
      200:
        description: Возвращает данные пользователя
        schema:
         $ref: '#/definitions/WhoOutputData'
    tags:
      - auth
    """
    jti = get_jwt()
    return {
        "auth": True,
        "user": {
            'email': jti['email'],
            'first_name': jti['first_name'],
            'last_name': jti['last_name'],
            'sub': jti['sub'],
            'role_names': jti['role_names'],
        }
    }


@bp.route('/register', methods=['POST'])
@api_error_handling_wrapper
def register():
    """Регистрация нового пользователя
    ---
    description: Необходимо предоставить данные пользователя
    parameters:
      - in: body
        schema:
          $ref: '#/definitions/RegisterInput'
    responses:
      200:
        description: Возвращает данные нового пользователя
        schema:
         $ref: '#/definitions/User'
    tags:
      - auth
    """
    json_input = request.json
    try:
        register_data = register_input_schema.load(json_input)
    except ValidationError as err:
        raise BadRequest(str(err.messages))

    email = register_data.get("email", None)
    password = register_data.get("password", None)
    first_name = register_data.get("first_name", None)
    last_name = register_data.get("last_name", None)
    phone = register_data.get("phone", None)

    user_service = UserService(db)
    if user_service.is_user_exists(email):
        raise BadRequest(f'User with email {email} already exists')

    new_user = user_service.create_user(
        email=email, password=password, first_name=first_name,
        last_name=last_name, phone=phone
    )

    return user_schema.dumps(new_user)


@api_error_handling_wrapper
@bp.route('/login', methods=['POST'])
@trace(span_name='login view')
def login():
    """Точка входа для существующего пользователя
    ---
    description: Необходимо предоставить логин и пароль
    definitions:
      LoginInputData:
        type: object
        required:
          - login
          - password
        properties:
          login:
            type: string
            description: Логин
          password:
            type: string
      LoginOutputData:
        type: object
        properties:
          access_token:
            type: string
          refresh_token:
            type: string
    parameters:
      - in: body
        schema:
          $ref: '#/definitions/LoginInputData'
    responses:
      200:
        description: Возвращает access_token и refresh_token
        schema:
         $ref: '#/definitions/LoginOutputData'
    tags:
      - auth
    """
    json_input = request.json

    try:
        login_data = login_input_schema.load(json_input)
    except ValidationError as err:
        raise BadRequest(str(err.messages))

    req_login = login_data.get("login", None)
    req_password = login_data.get("password", None)
    user_agent = request.headers['User-agent']
    ip = request.remote_addr

    auth_service = AuthService(db)
    data = auth_service.login(req_login, req_password, user_agent, ip)

    return data


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@api_error_handling_wrapper
def refresh():
    """Обновляет токен
    ---
    description: Обновляет токен
    responses:
      200:
        description: Возвращает access_token и refresh_token
        schema:
         $ref: '#/definitions/LoginOutputData'
    tags:
      - auth
    """

    refresh_token = request.headers['Authorization'].split(' ')[1]
    identity = get_jwt_identity()

    auth_service = AuthService(db)
    data = auth_service.refresh(identity, refresh_token)
    return data


@bp.route("/logout", methods=["POST"])
@api_error_handling_wrapper
@jwt_required()
def logout():
    """Разлогинивает текущего пользователя
    ---
    description: Разлогинивает текущего пользователя
    responses:
      200:
        description: Разлогинивает текущего пользователя
    tags:
      - auth
    """
    jwt = get_jwt()

    auth_service = AuthService(db)
    logout_result = auth_service.logout(user_id=jwt['sub'],
                                        jti=jwt["jti"])

    return {"msg": "Access token revoked"} if logout_result else None
