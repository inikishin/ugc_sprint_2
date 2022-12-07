from http import HTTPStatus
import pytest
from pydantic import ValidationError

from functional.utils.validation_models.movies import FilmShort, Person

pytestmark = pytest.mark.asyncio


async def test_persons_search_incorrect_page_number(
    make_get_request, load_data
):
    response = await make_get_request('/persons/search', {
        'query': 'person',
        'page[number]': 'abc',
        'page[size]': '3',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_persons_search_incorrect_page_size(make_get_request, load_data):
    response = await make_get_request('/persons/search', {
        'query': 'person',
        'page[number]': '1',
        'page[size]': 'abc',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_persons_search(make_get_request, load_data):
    response = await make_get_request('/persons/search', {
        'query': 'person',
        'page[number]': '1',
        'page[size]': '20',
    })

    assert response.status == HTTPStatus.OK
    assert len(response.body) > 0
    try:
        Person(**response.body[0])
        assert True
    except ValidationError:
        assert False


async def test_persons_single(make_get_request, load_data):
    response = await make_get_request('/persons/search', {
        'query': 'person',
        'page[number]': '1',
        'page[size]': '20',
    })

    person_id = response.body[0].get('uuid')

    response = await make_get_request(f'/persons/{person_id}')

    assert response.status == HTTPStatus.OK
    try:
        Person(**response.body)
        assert True
    except ValidationError:
        assert False


async def test_persons_films_single(make_get_request, load_data):
    response = await make_get_request('/persons/search', {
        'query': 'test person 1',
        'page[number]': '1',
        'page[size]': '20',
    })

    person_id = response.body[0].get('uuid')

    response = await make_get_request(f'/persons/{person_id}/film')

    assert response.status == HTTPStatus.OK
    try:
        FilmShort(**response.body[0])
        assert True
    except ValidationError:
        assert False


async def test_persons_single_wrong_id(make_get_request, load_data):
    person_id = '36930692-1978-475a-8f55-bbe32859b94f'

    response = await make_get_request(f'/persons/{person_id}')

    assert response.status == HTTPStatus.NOT_FOUND
