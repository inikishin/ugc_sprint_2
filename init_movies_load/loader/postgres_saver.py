import psycopg2.extras

psycopg2.extras.register_uuid()

table_fields = {
    "film_work": ['id', 'title', 'description', 'creation_date', 'rating',
                  'type', 'created', 'modified'],
    "genre": ['id', 'name', 'description', 'created', 'modified'],
    "genre_film_work": ['id', 'film_work_id', 'genre_id', 'created'],
    "person": ['id', 'full_name', 'created', 'modified'],
    "person_film_work": ['id', 'film_work_id', 'person_id', 'role', 'created'],
}


class PostgresSaver:
    def __init__(self, pg_conn):
        self.pg_conn = pg_conn

    def save_all_data(self, table_name, data: dict):
        cursor = self.pg_conn.cursor()

        fields = table_fields.get(table_name)
        field_names = ','.join(fields)
        update_fields = ','.join([f'{f}=%({f})s' for f in fields])
        values = ','.join([f'%({s})s' for s in fields])

        sql_query = """ insert into content.{0} ({1})
                        values({2})
                        ON CONFLICT (id) DO UPDATE SET {3};
        """.format(table_name, field_names, values, update_fields)
        print(sql_query)
        print(data[0]['id'])

        data_for_save = []
        for row in data:
            new_row = dict(**row)
            if 'created_at' in new_row:
                new_row['created'] = new_row['created_at']
                del new_row['created_at']

            if 'updated_at' in new_row:
                new_row['modified'] = new_row['updated_at']
                del new_row['updated_at']

            data_for_save.append(new_row)

        cursor.executemany(sql_query, data_for_save)

    def get_table_count(self, table_name):
        curs = self.pg_conn.cursor()
        curs.execute("SELECT count(*) FROM content.{0};".format(table_name))
        records = curs.fetchall()
        return records[0][0]

    def get_table_data(self, table_name):
        curs = self.pg_conn.cursor()
        curs.execute("SELECT * FROM content.{0};".format(table_name))
        records = curs.fetchall()
        return records

    def get_table_record_by_id(self, table_name, id):
        curs = self.pg_conn.cursor()
        curs.execute("SELECT * FROM content.{0} where id='{1}';".format(table_name, id))
        records = curs.fetchall()
        record = None
        if len(records) > 0:
            record = records[0]

        return record
