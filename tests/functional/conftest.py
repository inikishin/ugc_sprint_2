import sys
import os
import pytest
from typing import Optional
from dataclasses import dataclass

from multidict import CIMultiDictProxy
from elasticsearch import AsyncElasticsearch
from fastapi.testclient import TestClient
from httpx import AsyncClient
from asyncio import get_event_loop

sys.path.extend(['/data/async_api', '/data/tests/functional', '/data/auth_api'])

from core.config import cfg  # noqa: E402
from db.cache import cache  # noqa: E402
from main import app, startup  # noqa: E402
from utils.elastic_helper import generate_bulk_body  # noqa E402
from testdata.films_data import (  # noqa E402
    films_data, persons_data, genres_data)  # noqa E402
from auth.main import app as auth_app


SERVICE_URL = 'http://{host}:{port}'.format(
    host=os.getenv('API_HOST', '127.0.0.1'),
    port=os.getenv('API_PORT', 8000)
)


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture
async def client():
    api_client = TestClient(app)
    await startup()
    yield api_client


@pytest.fixture(scope='module')
async def async_client():
    async with AsyncClient(app=app, base_url=SERVICE_URL) as api_client:
        await startup()
        yield api_client


@pytest.fixture(scope='module')
def event_loop():
    loop = get_event_loop()
    yield loop


@pytest.fixture
async def cache_fixture():
    await cache.clear()
    yield cache
    await cache.close()


@pytest.fixture
def make_get_request(async_client):
    async def inner(
            method: str, params: Optional[dict] = None) -> HTTPResponse:
        params = params or {}
        url = SERVICE_URL + '/api/v1' + method
        response = await async_client.get(url, params=params)
        return HTTPResponse(
            body=response.json(),
            headers=response.headers,
            status=response.status_code,
        )
    return inner


@pytest.fixture(scope='session')
async def es_client():
    elastic_conn_string = 'http://{user}:{password}@{host}:{port}/'.format(
        user=cfg.ELASTIC_USERNAME,
        password=cfg.ELASTIC_PASSWORD,
        host=cfg.ELASTIC_HOST,
        port=cfg.ELASTIC_PORT
    )
    client = AsyncElasticsearch(
        hosts=[elastic_conn_string]
    )
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def load_data(es_client):
    genres_body = generate_bulk_body('genres', genres_data)
    await es_client.bulk(genres_body, refresh='true')

    persons_body = generate_bulk_body('persons', persons_data)
    await es_client.bulk(persons_body, refresh='true')

    films_body = generate_bulk_body('movies', films_data)
    await es_client.bulk(films_body, refresh='true')


@pytest.fixture(scope='session')
def auth_app_init():
    auth_app.config.update({
        "TESTING": True,
    })

    yield auth_app


@pytest.fixture(scope='session')
def auth_client(auth_app_init):
    return auth_app.test_client()


@pytest.fixture(scope='session')
def auth_runner(auth_app_init):
    return auth_app.test_cli_runner()


@pytest.fixture(scope='session')
def auth_with_superuser(auth_runner):
    auth_runner.invoke(
        args='command createsuperuser',
        input='\n'.join(
            ['test@email.com', 'first', 'admin', 'test', 'test', 'y']))

    yield


@pytest.fixture
def auth_get_headers(auth_client, auth_with_superuser):
    response_login = auth_client.post('/auth/login', json={
        'login': 'test@email.com',
        'password': 'test'
    })

    return {
        'Authorization':
            'Bearer ' + response_login.json['access_token']
    }


@pytest.fixture
def auth_get_headers_for_refresh(auth_client, auth_with_superuser):
    response_login = auth_client.post('/auth/login', json={
        'login': 'test@email.com',
        'password': 'test'
    })

    return {
        'Authorization':
            'Bearer ' + response_login.json['refresh_token']
    }
