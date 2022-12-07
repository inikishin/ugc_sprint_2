"""JSON Layout responses"""

from flask import make_response, Response

from auth.main import app


def json_get_list_response(data: list, total: int = None) -> Response:
    """
    Create json success response on GET request of data collection accordingly
    with JSON API specification https://jsonapi.org/format/#error-objects

    :param data: list of data to return

    :return: Flask Response object via make_response function
    https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.make_response
    """
    response = {
        "data": data if data else []
    }

    if total:
        response['total'] = total

    return make_response(
        (
            response,
            200,
        )
    )


def json_get_item_response(item: dict) -> Response:
    """GET item JSON response"""
    return make_response(
        (
            {"data": item},
            200,
        )
    )


def json_post_response(item: dict) -> Response:
    """POST item JSON response"""
    with app.app_context():
        return make_response(
            (
                {"data": item},
                200,
            )
        )


def json_put_response(item: dict) -> Response:
    """PUT item JSON response"""
    with app.app_context():
        return make_response(
            (
                {"data": item},
                200,
            )
        )


def json_delete_response(status: bool) -> Response:
    """DELETE item JSON response"""
    with app.app_context():
        return make_response(
            (
                {"data":
                     {"status": status}
                 },
                200,
            )
        )


def json_error_response(status: int,
                              code: str,
                              title: str,
                              detail: str) -> Response:
    """
    Create json error response accordingly with JSON API specification
    https://jsonapi.org/format/#error-objects

    :param status: the HTTP status code applicable to this problem
    :param code: an application-specific error code
    :param title: a short, human-readable summary of the problem that SHOULD
    NOT change from occurrence to occurrence of the problem
    :param detail: a human-readable explanation specific to this occurrence of
    the problem
    :return: Flask Response object via make_response function
    https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.make_response
    """
    with app.app_context():
        return make_response(
            (
                {
                    "errors": [
                        {
                            "status": str(status),
                            "code": code,
                            "title": title,
                            "detail": detail,
                        }
                    ]
                },
                status,
            )
        )
