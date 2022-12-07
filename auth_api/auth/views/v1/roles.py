from flask import request, Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt

from auth.models import db
from auth.services.roles import RoleService
from auth.views.schemas import role_schema, roles_schema
from auth.utils.api_error_handling_wrapper import api_error_handling_wrapper
from auth.utils.rbac import current_identity, allow

bp = Blueprint('roles', __name__, url_prefix='/roles')


class RolesAPI(MethodView):
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    decorators = [api_error_handling_wrapper, jwt_required()]

    @allow(['admin', 'user'])
    def get(self, role_id: str):
        """Получение данных о ролях
        ---
        description: Получение данных об одной или нескольких ролях
        responses:
          200:
            description: Возвращает данные о ролях
            schema:
              $ref: '#/definitions/Role'
        tags:
          - roles
        """
        role_service = RoleService(db)

        if role_id:
            role = role_service.get_role_by_id(role_id)
            return role_schema.dumps(role)
        else:
            roles = role_service.get_all_roles()
            return roles_schema.dumps(roles, many=True)


    @allow(['admin'])
    def post(self):
        """Создание роли
        ---
        description: Создаем новую роль
        definitions:
          RoleInputData:
            type: object
            required:
              - name
            properties:
              name:
                type: string
                description: Имя
              description:
                type: string
                description: Описание
        parameters:
          - in: body
            schema:
              $ref: '#/definitions/RoleInputData'
        responses:
          200:
            description: Возвращает данные успешно созданной роли
            schema:
              $ref: '#/definitions/Role'
        tags:
          - roles
        """
        role_service = RoleService(db)
        role_name = request.json.get("name", None)
        role_description = request.json.get("description", None)

        new_role = role_service.create_role(role_name, role_description)

        return role_schema.dumps(new_role)

    @allow(['admin'])
    def put(self, role_id):
        """Изменение данных роли
        ---
        description: Изменение данных роли
        parameters:
          - name: role_id
            in: path
            type: string
            required: true
          - in: body
            schema:
              $ref: '#/definitions/RoleInputData'
        responses:
          200:
            description: Возвращает обновленные данные роли
            schema:
              $ref: '#/definitions/Role'
        tags:
          - roles
        """
        role_service = RoleService(db)
        role_name = request.json.get("name", None)
        role_description = request.json.get("description", None)

        updated_role = role_service.update_role(role_id,
                                                role_name,
                                                role_description)

        return role_schema.dumps(updated_role)

    @allow(['admin'])
    def delete(self, role_id):
        """Удаление роли
        ---
        description: Удаление роли
        parameters:
          - name: role_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Успешное удаление роли
        tags:
          - roles
        """
        role_service = RoleService(db)

        deleted = role_service.delete_role(role_id)

        return {'msg': 'Role deleted'} if deleted else None


view = RolesAPI.as_view('roles_api')
bp.add_url_rule('',
                defaults={'role_id': None},
                view_func=view,
                methods=['GET', 'POST'])
bp.add_url_rule('', view_func=view, methods=['POST', ])
bp.add_url_rule('/<uuid:role_id>',
                view_func=view,
                methods=['GET', 'PUT', 'DELETE'])
