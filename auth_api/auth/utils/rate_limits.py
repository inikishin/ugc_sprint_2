import datetime
import os

from flask_jwt_extended import get_jwt
import redis

REQUEST_LIMIT_PER_MINUTE = int(os.getenv('REQUEST_LIMIT_PER_MINUTE', 5))

redis_conn = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', '6379')),
    db=os.getenv('REDIS_DB_RATE_LIMITS', 3))


def limit_leaky_bucket(func):
    """Rate limit controller with leaky bucket strategy"""
    def limit_leaky_bucket_wrapper():
        jti = get_jwt()

        pipe = redis_conn.pipeline()
        now = datetime.datetime.now()
        key = f'{jti["sub"]}:{now.minute}'
        pipe.incr(key, 1)
        pipe.expire(key, 59)
        result = pipe.execute()

        request_number = result[0]
        if request_number > REQUEST_LIMIT_PER_MINUTE:
            return {'msg': f'Too many requests ({request_number})'}, 429
        else:
            return func()

    limit_leaky_bucket_wrapper.__name__ = func.__name__
    return limit_leaky_bucket_wrapper
