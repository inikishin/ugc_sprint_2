import sqlite3

class SQLiteLoader:
    def __init__(self, connection):
        self.connection = connection
        self.connection.row_factory = sqlite3.Row
        self.tables = ['genre', 'person', 'film_work', 'genre_film_work', 'person_film_work']

    def load_movies(self, table_name):
        curs = self.connection.cursor()
        curs.execute("SELECT * FROM {0};".format(table_name))

        return curs

    def get_table_count(self, table_name):
        curs = self.connection.cursor()
        curs.execute("SELECT count(*) as count FROM {0};".format(table_name))
        records = curs.fetchall()
        return dict(records[0]).get('count')