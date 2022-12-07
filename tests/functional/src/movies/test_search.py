from http import HTTPStatus
import pytest
from pydantic import ValidationError

from functional.utils.validation_models.movies import FilmShort

pytestmark = pytest.mark.asyncio


async def test_search_query_text(make_get_request, load_data):
    response = await make_get_request(
        '/films/search',
        {'query': 'test title 3'})

    assert response.status == HTTPStatus.OK
    assert len(response.body) > 1
    try:
        FilmShort(**response.body[0])
        assert True
    except ValidationError:
        assert False


async def test_search_get_three_records(make_get_request, load_data):
    response = await make_get_request('/films/search', {
        'query': 'test',
        'page[number]': '1',
        'page[size]': '3',
    })

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3


async def test_search_incorrect_page_number(make_get_request, load_data):
    response = await make_get_request('/films/search', params={
        'query': 'test',
        'page[number]': 'abc',
        'page[size]': '3',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_search_incorrect_page_size(make_get_request, load_data):
    response = await make_get_request('/films/search', params={
        'query': 'test',
        'page[number]': '1',
        'page[size]': 'abc',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY
