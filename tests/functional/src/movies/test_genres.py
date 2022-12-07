from http import HTTPStatus
import pytest
from pydantic import ValidationError

from functional.utils.validation_models.movies import Genre

pytestmark = pytest.mark.asyncio


async def test_genres_incorrect_page_number(make_get_request, load_data):
    response = await make_get_request('/genres/', {
        'page[number]': 'abc',
        'page[size]': '3',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_genres_incorrect_page_size(make_get_request, load_data):
    response = await make_get_request('/genres/', {
        'page[number]': '1',
        'page[size]': 'abc',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_genres_all(make_get_request, load_data):
    response = await make_get_request('/genres/', {
        'page[number]': '1',
        'page[size]': '3',
    })

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3
    try:
        Genre(**response.body[0])
        assert True
    except ValidationError:
        assert False


async def test_genres_single(make_get_request, load_data):
    response = await make_get_request('/genres/', {
        'page[number]': '1',
        'page[size]': '20',
    })

    genre_id = response.body[0].get('uuid')

    response = await make_get_request(f'/genres/{genre_id}', {
        'page[number]': '1',
        'page[size]': '20',
    })

    assert response.status == HTTPStatus.OK
    try:
        Genre(**response.body)
        assert True
    except ValidationError:
        assert False


async def test_genres_single_wrong_id(make_get_request, load_data):
    genre_id = '36930692-1978-475a-8f55-bbe32859b94f'

    response = await make_get_request(f'/genres/{genre_id}', {
        'page[number]': '1',
        'page[size]': '20',
    })

    assert response.status == HTTPStatus.NOT_FOUND
