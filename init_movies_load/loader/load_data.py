import os
import logging
from dotenv import load_dotenv
import sqlite3
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from postgres_saver import PostgresSaver
from sqlite_loader import SQLiteLoader

load_dotenv()


@contextmanager
def open_db(file_name: str):
    conn = sqlite3.connect(file_name)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    batch_size = int(os.getenv('BATCH_SIZE'))

    for table_name in sqlite_loader.tables:
        cursor = sqlite_loader.load_movies(table_name)
        data = cursor.fetchmany(batch_size)
        while data:
            postgres_saver.save_all_data(table_name, data)
            data = cursor.fetchmany(batch_size)

    logging.debug(data)


if __name__ == '__main__':
    dsl = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }
    with open_db(file_name=os.getenv('SQLITE_PATH')) as sqlite_conn, \
            psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
