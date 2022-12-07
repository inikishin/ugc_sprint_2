#!/usr/bin/env python3

import sys
import os
import dataclasses
import logging
import time
from typing import Optional

import redis
from pydantic.dataclasses import dataclass

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class RedisConf:
    host: str = os.environ.get('REDIS_HOST', '127.0.0.1')
    port: int = int(os.environ.get('REDIS_PORT', 6379))
    password: Optional[str] = os.environ.get('REDIS_PASSWORD')


MAX_TIMEOUT_SECONDS = 30


def main():

    start_timestamp = int(time.time())

    redis_conf = dataclasses.asdict(RedisConf())
    redis_adapter = redis.StrictRedis(**redis_conf)

    while True:
        try:
            redis_adapter.ping()
            logging.info('redis is ready.')
            break
        except redis.ConnectionError:
            logging.info('waiting for redis...')
            time.sleep(0.5)

        if int(time.time()) - start_timestamp > MAX_TIMEOUT_SECONDS:
            logging.error('resource is not available')
            sys.exit(1)


if __name__ == '__main__':
    main()
