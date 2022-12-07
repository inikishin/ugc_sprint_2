from marshmallow import fields
from auth.main import ma


class UserSchema(ma.Schema):
    id = fields.Str(required=True, description='id')
    email = fields.Str(required=True, description='email')
    first_name = fields.Str(required=True, description='Имя')
    last_name = fields.Str(required=True, description='Фамилия')
    phone = fields.Str(required=True, description='Телефон')

    def role_names(self, obj):
        return [role.role.name for role in obj.roles]


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class RoleSchema(ma.Schema):
    id = fields.Str(required=True, description='id')
    name = fields.Str(required=True, description='Название роли')
    description = fields.Str(required=True, description='Описание роли')


role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)


class UserLoginHistorySchema(ma.Schema):
    class Meta:
        fields = ['id', 'user_id', 'user_agent', 'login_ip', 'login_at']

    id = fields.Str(required=True, description='id')
    user_id = fields.Str(required=True, description='id пользователя')
    user_agent = fields.Str(required=True, description='User Agent браузера')
    login_ip = fields.Str(required=True, description='IP')
    login_at = fields.Int(required=True, description='Время логина')


user_login_history_schema = UserLoginHistorySchema(many=True)


class LoginInput(ma.Schema):
    login = fields.Str(required=True, description='Логин')
    password = fields.Str(required=True, description='Пароль')

login_input_schema = LoginInput()


class RegisterInput(ma.Schema):
    email = fields.Str(required=True, description='email')
    password = fields.Str(required=True, description='Пароль')
    first_name = fields.Str(required=True, description='Имя')
    last_name = fields.Str(required=True, description='Фамилия')
    phone = fields.Str(required=True, description='Телефон')

register_input_schema = RegisterInput()
