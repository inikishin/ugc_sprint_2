from flask import request, Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from auth.models import db
from auth.services.users import UserService
from auth.views.schemas import roles_schema, user_schema, users_schema, user_login_history_schema
from auth.utils.api_error_handling_wrapper import api_error_handling_wrapper
from auth.utils.rate_limits import limit_leaky_bucket
from auth.utils.rbac import allow

bp = Blueprint('users', __name__, url_prefix='/users')


class UsersAPI(MethodView):
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    decorators = [api_error_handling_wrapper, jwt_required()]

    @allow(['admin', 'user'])
    def get(self, user_id: str):
        """Получение данных о пользователях
        ---
        description: Получение данных об одном или нескольких пользователях
        responses:
          200:
            description: Возвращает данные о пользователях
            schema:
              $ref: '#/definitions/User'
        tags:
          - users
        """
        user_service = UserService(db)

        if user_id:
            user = user_service.get_user_by_id(user_id)
            return user_schema.dumps(user)
        else:
            users = user_service.get_all_users()
            return users_schema.dumps(users)

    def post(self):
        """Создание пользователя
        ---
        description: Создаем нового пользователя
        definitions:
          UserInputData:
            type: object
            required:
              - login
              - password
            properties:
              email:
                type: string
                description: email
              password:
                type: string
                description: Пароль
              first_name:
                type: string
                description: Имя
              last_name:
                type: string
                description: Фамилия
              phone:
                type: string
                description: Телефон
        parameters:
          - in: body
            schema:
              $ref: '#/definitions/UserInputData'
        responses:
          200:
            description: Возвращает данные успешно созданного пользователя
            schema:
              $ref: '#/definitions/User'
        tags:
          - users
        """
        user_service = UserService(db)

        user_email = request.json.get("email", None)
        user_password = request.json.get("password", None)
        user_first_name = request.json.get("first_name", None)
        user_last_name = request.json.get("last_name", None)
        user_phone = request.json.get("phone", None)

        new_user = user_service.create_user(email=user_email,
                                            password=user_password,
                                            first_name=user_first_name,
                                            last_name=user_last_name,
                                            phone=user_phone)

        return user_schema.dumps(new_user)

    def put(self, user_id: str):
        """Изменение данных пользователя
        ---
        description: Изменение данных пользователя
        parameters:
          - name: user_id
            in: path
            type: string
            required: true
          - in: body
            schema:
              $ref: '#/definitions/UserInputData'
        responses:
          200:
            description: Возвращает обновленные данные пользователя
            schema:
              $ref: '#/definitions/User'
        tags:
          - users
        """
        user_service = UserService(db)

        updated_user = user_service.update_user(user_id=user_id,
                                                user_data=request.json)

        return user_schema.dumps(updated_user)

    def delete(self, user_id: str):
        """Удаление пользователя
        ---
        description: Удаление пользователя
        parameters:
          - name: user_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Успешное удаление пользователя
        tags:
          - users
        """
        user_service = UserService(db)

        deleted = user_service.deactivate_user(user_id)

        return {'msg': 'user deleted'} if deleted else None


@bp.route('/<uuid:user_id>/roles', methods=['GET'])
@api_error_handling_wrapper
@limit_leaky_bucket
@allow(['user', 'admin'])
def get_user_roles(user_id):
    """Возвращает текущие роли пользователя
    ---
    description: Возвращает текущие роли пользователя
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    definitions:
      UserRoles:
        type: array
        items:
          type: string
    responses:
      '200':
        description: Список ролей пользователя
        schema:
          $ref: '#/definitions/UserRoles'
    tags:
      - users
    """
    user_service = UserService(db)
    roles = user_service.get_user_roles(user_id)

    return roles_schema.dumps(roles)


@bp.route('/<uuid:user_id>/login-history', methods=['GET'])
@api_error_handling_wrapper
@limit_leaky_bucket
@allow(['user', 'admin'])
def get_user_login_history(user_id):
    """Возвращает историю логинов пользователя
    ---
    description: Возвращает историю логинов пользователя
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      '200':
        description: Список истории логинов пользователя
        schema:
          $ref: '#/definitions/UserLoginHistory'
    tags:
      - users
    """
    page_number = int(request.args.get('page[number]', 1))
    page_size = int(request.args.get('page[size]', 100))
    user_service = UserService(db)
    history = user_service.get_user_login_history(user_id,
                                                  page_number,
                                                  page_size)

    return user_login_history_schema.dumps(history)


@bp.route('/<uuid:user_id>/add-role', methods=['POST'])
@api_error_handling_wrapper
@limit_leaky_bucket
@allow(['admin'])
def add_role_to_user(user_id):
    """Добавляет роль пользователю
    ---
    description: Добавляет роль пользователю
    definitions:
      UserRoleInputData:
        type: object
        required:
          - role_id
        properties:
          role_id:
            type: string
            description: role_id
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - in: body
        schema:
          $ref: '#/definitions/UserRoleInputData'
    responses:
      '200':
        description: Роль добавлена
    tags:
      - users
    """
    role_id = request.json.get("role_id", None)

    user_service = UserService(db)
    link_id = user_service.add_role_to_user(user_id, role_id)

    return {'msg': 'Role added'} if link_id else None


@bp.route('/<uuid:user_id>/remove-role', methods=['POST'])
@api_error_handling_wrapper
@limit_leaky_bucket
@allow(['admin'])
def remove_role_from_user(user_id):
    """Удаляет роль пользователю
    ---
    description: Удаляет роль пользователю
    definitions:
      UserRoleInputData:
        type: object
        required:
          - role_id
        properties:
          role_id:
            type: string
            description: role_id
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
      - in: body
        schema:
          $ref: '#/definitions/UserRoleInputData'
    responses:
      '200':
        description: Роль удалена
    tags:
      - users
    """
    role_id = request.json.get("role_id", None)

    user_service = UserService(db)
    success = user_service.remove_role_to_user(user_id, role_id)

    return {'msg': 'Role removed'} if success else None


view = UsersAPI.as_view('users_api')
bp.add_url_rule('',
                defaults={'user_id': None},
                view_func=view,
                methods=['GET', 'POST'])
bp.add_url_rule('', view_func=view, methods=['POST', ])
bp.add_url_rule('/<uuid:user_id>',
                view_func=view,
                methods=['GET', 'PUT', 'DELETE'])
