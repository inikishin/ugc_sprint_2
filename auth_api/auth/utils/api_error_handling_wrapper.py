"""Error handler wrapper for all view endpoints"""
from functools import wraps
from sqlalchemy.exc import NoResultFound
from werkzeug.exceptions import NotFound, BadRequest, Forbidden, Unauthorized
from auth.main import logger
from auth.utils.api_responses import json_error_response


def api_error_handling_wrapper(func):
    """API error handling wrapper"""

    @wraps(func)  # To make sure function with different name is returned for different deco calls
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequest as error:
            logger.error(error)
            return json_error_response(status=400,
                                       code='Bad Request',
                                       title=error.__class__.__name__,
                                       detail=error.description)
        except Unauthorized as error:
            logger.error(error)
            return json_error_response(status=401,
                                       code='Unauthorized',
                                       title=error.__class__.__name__,
                                       detail=error.description)
        except Forbidden as error:
            logger.error(error)
            return json_error_response(status=403,
                                       code='Forbidden',
                                       title=error.__class__.__name__,
                                       detail=error.description)
        except (NoResultFound, NotFound) as error:
            logger.error(error)
            return json_error_response(status=404,
                                       code='Not Found',
                                       title=error.__class__.__name__,
                                       detail=', '.join(error.args))
        except Exception as error:
            logger.error(error)
            return json_error_response(status=500,
                                       code='Internal Server Error',
                                       title=error.__class__.__name__,
                                       detail=', '.join(error.args))

    wrapper.__name__ = func.__name__
    return wrapper
