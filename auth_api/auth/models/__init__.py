import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def get_pg_auth_uri():
    user = os.getenv('PG_AUTH_USER', 'app')
    password = os.getenv('PG_AUTH_PASS', '123qwe')
    db_name = os.getenv('PG_AUTH_DB', 'auth_database')
    host = os.getenv('PG_AUTH_HOST', 'localhost')
    port = os.getenv('PG_AUTH_PORT', '5431')
    return f'postgresql://{user}:{password}@{host}:{port}/{db_name}'


engine = create_engine(get_pg_auth_uri(), convert_unicode=True)
db = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db.query_property()


