import sqlite3
import psycopg2
import logger
from uuid import UUID
from datetime import datetime
from psycopg2.extras import DictCursor

from sqlite_loader import SQLiteLoader
from postgres_saver import PostgresSaver

dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}


def test_count():
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        sqlite_loader = SQLiteLoader(sqlite_conn)
        postgres_saver = PostgresSaver(pg_conn)

        lite_count = {}
        pg_count = {}
        for table in sqlite_loader.tables:
            lite_count[table] = sqlite_loader.get_table_count(table)
            pg_count[table] = postgres_saver.get_table_count(table)

        logger.debug(lite_count)
        logger.debug(pg_count)
        assert lite_count == pg_count


def test_content():
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        sqlite_loader = SQLiteLoader(sqlite_conn)
        postgres_saver = PostgresSaver(pg_conn)

        checked = True

        sqlite_data = sqlite_loader.load_movies()
        for table_name in sqlite_data.keys():
            for sqlite_rec in sqlite_data[table_name]:
                pg_record = postgres_saver.get_table_record_by_id(table_name, sqlite_rec.get('id'))
                if pg_record:
                    for field in pg_record.keys():
                        pg_field = pg_record.get(field)
                        sq_field = sqlite_rec.get(field)
                        if type(pg_field) == UUID:
                            pg_field = str(pg_field)

                        if type(pg_field) == datetime:
                            sq_field = sqlite_rec.get(field).split('.')[0]
                            pg_field = pg_field.strftime("%Y-%m-%d %H:%M:%S")

                        if sq_field != pg_field:
                            checked = False
                            logger.debug('Table: {0} | field not equal {1} | record: {2} || {3}'.format(table_name,
                                                                                                 field,
                                                                                                 sqlite_rec,
                                                                                                 pg_record))
                else:
                    logger.debug('Table: {0} | Record {1} not found in pg base'.format(table_name, sqlite_rec))
                    checked = False

        assert checked
