import pytest
from pydantic import ValidationError

from functional.utils.validation_models.auth import AuthTokens, WhoResponse


def test_auth_who_without_authorization(auth_client):
    """Тестируем ответ от сервера авторизации при неавторизованном запросе."""
    response = auth_client.get('/auth/who')

    assert response.status == '401 UNAUTHORIZED'


def test_auth_login(auth_client, auth_with_superuser):
    """Тестируем логин существующим пользователем."""
    response = auth_client.post('/auth/login', json={
        'login': 'test@email.com',
        'password': 'test'
    })

    assert response.status == '200 OK'

    try:
        AuthTokens(**response.json)
        assert True
    except ValidationError:
        assert False


def test_auth_who(auth_client, auth_get_headers):
    """Тестируем ответ от сервера авторизации при авторизованном запросе."""
    response = auth_client.get('/auth/who', headers=auth_get_headers)

    assert response.status == '200 OK'

    try:
        WhoResponse(**response.json)
        assert True
    except ValidationError:
        assert False


def test_auth_refresh_success(auth_client, auth_get_headers_for_refresh):
    """Тестируем ответ от сервера авторизации при обновлении токена."""
    response = auth_client.post('/auth/refresh', headers=auth_get_headers_for_refresh)

    assert response.status == '200 OK'

    try:
        AuthTokens(**response.json)
        assert True
    except ValidationError:
        assert False


def test_auth_refresh_with_old_token(auth_client, auth_get_headers_for_refresh):
    """Тестируем ответ от сервера авторизации при обновлении токена второй раз
    c тем же refresh_token.
    """
    response = auth_client.post('/auth/refresh',
                                headers=auth_get_headers_for_refresh)
    response = auth_client.post('/auth/refresh',
                                headers=auth_get_headers_for_refresh)

    assert response.status == '401 UNAUTHORIZED'


def test_register_success(auth_client):
    """Тестируем успешную регистрацию пользователя."""
    response = auth_client.post('/auth/register', json={
        'email': 'test1@email.com',
        'password': 'test',
        'first_name': 'first_test',
        'last_name': 'last_test',
        'phone': '123456',
    })

    assert response.status == '200 OK'


def test_register_with_used_email(auth_client, auth_with_superuser):
    """Тестируем регистрацию пользователя, если email уже занят."""
    response = auth_client.post('/auth/register', json={
        'email': 'test@email.com',
        'password': 'test',
        'first_name': 'first_test',
        'last_name': 'last_test',
        'phone': '123456',
    })

    assert response.status == '400 BAD REQUEST'


def test_auth_logout_with_auth_headers(auth_client, auth_get_headers):
    """Тестируем ответ от сервера авторизации выходе из учетной записи, с
    корректным заголовком.
    """
    response = auth_client.post('/auth/logout', headers=auth_get_headers)

    assert response.status == '200 OK'


def test_auth_logout_without_auth_headers(auth_client):
    """Тестируем ответ от сервера авторизации выходе из учетной записи, с
    некорректным заголовком.
    """
    response = auth_client.post('/auth/logout')

    assert response.status == '500 INTERNAL SERVER ERROR'
    assert response.json['errors'][0]['title'] == 'NoAuthorizationError'
