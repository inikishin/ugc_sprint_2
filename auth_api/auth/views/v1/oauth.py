from flask import Blueprint, request

from auth.models import db
from auth.services.oauth import get_provider_service
from auth.services.oauth.yandex import YandexOAuthService
from auth.services.users import UserService
from auth.utils.rbac import allow, current_identity

PROVIDER = 'yandex'

bp = Blueprint('oauth', __name__, url_prefix='/oauth')


@bp.route('/<provider>/authorize-url', methods=['GET'])
def get_authorize_url(provider: str):
    """Возвращает url для авторизации."""
    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        return {'msg': 'Unknown provider'}, 400

    return {
        'authorize_url': oauth_service.get_authorize_url()
    }


@bp.route('/<provider>/webhook', methods=['GET'])
def receive_verification_code(provider: str):
    """Вебхук для редиректа после авторизации в яндексе."""
    verification_code = request.args.get('code', None)
    state = request.args.get('state', None)

    if verification_code is None:
        return {'msg': 'code not found in params'}

    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        return {'msg': 'Unknown provider'}, 400

    user_service = UserService(db)
    token_data = oauth_service.get_token(verification_code, state)

    if token_data.get('access_token') is None:
        return token_data, 400

    user_info = oauth_service.get_user_info(
        access_token=token_data.get('access_token'))

    user = user_service.get_user_by_universal_email(
        email=user_info.get('default_email'),
    )

    if user is None:
        user = user_service.create_user(
            email=user_info.get('default_email'),
            password='123', # TODO Сейчас хардкод, затем, после добавления сервиса уведомлений, отправка уведомления со сгенерированным паролем
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name'),
        )

    user_service.save_user_oauth_refresh_token(
        user.id,
        PROVIDER,
        token_data.get('refresh_token'),
        token_data.get('expires_in'))

    return {'user_id': user.id}


@bp.route('/<provider>/who', methods=['GET'])
@allow(['admin', 'user'])
def get_user_info(provider: str):
    """Ендпоинт возвращает информацию о пользователе с сервиса Yandex."""
    current_user = current_identity()
    user_service = UserService(db)

    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        return {'msg': 'Unknown provider'}, 400

    refresh_token = user_service.get_user_oauth_refresh_token(current_user.id,
                                                              PROVIDER)

    data = oauth_service.refresh_token(refresh_token=refresh_token)

    user_service.save_user_oauth_refresh_token(
        current_user.id,
        PROVIDER,
        data.get('refresh_token'),
        data.get('expires_in'))
    user_info = oauth_service.get_user_info(
        access_token=data.get('access_token'))

    if user_info is None:
        user_info = {'data': 'no data'}

    return user_info
