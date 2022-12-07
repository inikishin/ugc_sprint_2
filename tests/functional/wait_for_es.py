#!/usr/bin/env python3

import sys
import os
import logging
import time

import elasticsearch


es_logger = logging.getLogger('elasticsearch')
es_logger.setLevel(logging.ERROR)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


ELASTIC_CONN_STRING = "http://{user}:{password}@{host}:{port}/".format(
    user=os.environ.get('ELASTIC_USERNAME'),
    password=os.environ.get('ELASTIC_PASSWORD'),
    host=os.environ.get('ELASTIC_HOST'),
    port=os.environ.get('ELASTIC_PORT'),
)

MAX_TIMEOUT_SECONDS = 30


def main():

    start_timestamp = int(time.time())

    while True:
        try:
            connection = elasticsearch.Elasticsearch(ELASTIC_CONN_STRING)
            if connection.ping():
                logging.info('es is ready.')
                break
        except Exception:
            pass

        if int(time.time()) - start_timestamp > MAX_TIMEOUT_SECONDS:
            logging.error('resource is not available')
            sys.exit(1)

        logging.info('waiting for es...')
        time.sleep(2)


if __name__ == '__main__':
    main()
