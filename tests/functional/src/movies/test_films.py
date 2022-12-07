from http import HTTPStatus
import pytest
from pydantic import ValidationError

from functional.utils.validation_models.movies import FilmShort, Film

pytestmark = pytest.mark.asyncio


async def test_films_incorrect_page_number(make_get_request, load_data):
    response = await make_get_request('/films/', {
        'query': 'test',
        'page[number]': 'abc',
        'page[size]': '3',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_films_incorrect_page_size(make_get_request, load_data):
    response = await make_get_request('/films/', {
        'query': 'test',
        'page[number]': '1',
        'page[size]': 'abc',
    })

    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY


async def test_films_incorrect_sort(make_get_request, load_data):
    response = await make_get_request('/films/', {
        'sort': 'abc',
        'page[number]': '1',
        'page[size]': '50',
    })

    assert response.status == HTTPStatus.BAD_REQUEST


async def test_films_sort_desc(make_get_request, load_data):
    response = await make_get_request('/films/', {
        'sort': '-imdb_rating',
        'page[number]': '1',
        'page[size]': '100',
    })

    assert response.status == HTTPStatus.OK
    assert len(response.body) > 1

    first_rating = response.body[0].get('imdb_rating')
    last_rating = response.body[len(response.body) - 1].get('imdb_rating')

    assert first_rating >= last_rating


async def test_films_sort_asc(make_get_request, load_data):
    response = await make_get_request('/films/', {
        'sort': '+imdb_rating',
        'page[number]': '1',
        'page[size]': '100',
    })

    assert response.status == HTTPStatus.OK
    assert len(response.body) > 1

    first_rating = response.body[0].get('imdb_rating')
    last_rating = response.body[len(response.body) - 1].get('imdb_rating')

    assert first_rating <= last_rating


async def test_films_all(make_get_request, load_data):
    response = await make_get_request('/films/', {
        'page[number]': '1',
        'page[size]': '20',
    })

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3
    try:
        FilmShort(**response.body[0])
        assert True
    except ValidationError:
        assert False


async def test_films_single(make_get_request, load_data):
    response = await make_get_request('/films/', {
        'page[number]': '1',
        'page[size]': '20',
    })

    film_id = response.body[0].get('uuid')
    response = await make_get_request(f'/films/{film_id}', {
        'page[number]': '1',
        'page[size]': '20',
    })

    assert response.status == HTTPStatus.OK
    try:
        Film(**response.body)
        assert True
    except ValidationError:
        assert False


async def test_films_single_wrong_id(make_get_request, load_data):
    film_id = '36930692-1978-475a-8f55-bbe32859b94f'
    response = await make_get_request(f'/films/{film_id}', {
        'page[number]': '1',
        'page[size]': '20',
    })

    assert response.status == HTTPStatus.NOT_FOUND
