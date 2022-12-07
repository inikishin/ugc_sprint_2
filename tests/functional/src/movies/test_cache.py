from unittest.mock import patch

from http import HTTPStatus
import pytest

from services.films import ElasticFilmService
from services.genres import ElasticGenreService
from services.persons import ElasticPersonService
from testdata.films_data import persons_data_ids


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'endpoint', ['/films/', '/genres/', '/persons/{uuid}']
)
async def test_main_cache(
        make_get_request, cache_fixture, load_data, endpoint
):
    cache = cache_fixture
    await cache.clear()

    methods = {
        '/films/': {
            'class': ElasticFilmService,
            'side_effect': ElasticFilmService.get_films
        },
        '/genres/': {
            'class': ElasticGenreService,
            'side_effect': ElasticGenreService.get_genres
        },
        '/persons/{uuid}': {
            'class': ElasticPersonService,
            'side_effect': ElasticPersonService.get_by_id,
            'uuid': persons_data_ids[0]
        }
    }

    with patch.object(
            methods[endpoint]['class'],
            methods[endpoint]['side_effect'].__name__,
            side_effect=methods[endpoint]['side_effect'],
            autospec=True) as mocked_method:

        mocked_method.reset_mock()

        endpoint = endpoint.format(uuid=methods[endpoint].get('uuid'))

        # Первый запрос - берем данные из базы
        response = await make_get_request(endpoint)
        assert response.status == HTTPStatus.OK
        assert len(response.body) > 0
        assert mocked_method.await_count == 1

        cache_hits = cache.get_hits()
        cache_total = cache.get_total()

        # Второй запрос - берем данные из кэша
        response = await make_get_request(endpoint)
        assert response.status == HTTPStatus.OK
        assert len(response.body) > 0
        assert cache.get_hits() == cache_hits + 1
        assert cache.get_total() == cache_total + 1
        assert mocked_method.await_count == 1

        # Третий запрос - берем данные из кэша
        response = await make_get_request(endpoint)
        assert response.status == HTTPStatus.OK
        assert len(response.body) > 0
        assert cache.get_hits() == cache_hits + 2
        assert cache.get_total() == cache_total + 2
        assert mocked_method.await_count == 1

        await cache.clear()

        # Запрос после очистки кэша - берем данные из базы
        response = await make_get_request(endpoint)
        assert response.status == HTTPStatus.OK
        assert len(response.body) > 0
        assert cache.get_hits() == cache_hits + 2
        assert cache.get_total() == cache_total + 3
        assert mocked_method.await_count == 2

        await cache.clear()
