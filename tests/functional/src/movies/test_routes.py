from http import HTTPStatus


def test_main_pages(client):
    response = client.get('/api/openapi/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.text) > 0

    response = client.get('/api/v1/films/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.text) > 0

    response = client.get('/api/v1/genres/')
    assert response.status_code == HTTPStatus.OK
    assert len(response.text) > 0

    response = client.get('/api/v1/films/test/')
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    test_uuid = '5aefbab4-9245-4ab0-bcc8-6b224fa23080'
    response = client.get(f'/api/v1/films/{test_uuid}/')
    assert response.status_code == HTTPStatus.NOT_FOUND
