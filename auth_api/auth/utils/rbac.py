from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.exceptions import Forbidden

from auth.models import db
from auth.services.users import UserService


def current_identity():
    user_id = get_jwt_identity()
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)


def allow(roles):
    """
    Creates and returns a function decorator that authenticates based on JWT
    token and authorized role specified in the roles argument. If JWT token
    is valid and current user matches specified roles the decorator retuns
    original function (authenticated), otherwise, it returns 403 Forbidden.
    """
    def deco(func):
        @wraps(func)  # To make sure function with different name is returned for different deco calls
        @jwt_required()
        def inner(*args, **kwargs):
            user_id = get_jwt_identity()
            user_role_name = get_jwt()['role_names']
            if user_id and set(user_role_name).intersection(roles):
                return func(*args, **kwargs)
            else:
                raise Forbidden('Access denied. Insufficient permissions')

        return inner
    return deco
