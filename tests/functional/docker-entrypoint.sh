#!/usr/bin/env bash

set -e

DIR=/data/tests/functional

echo 'Waiting for services...'

python3 ${DIR}/wait_for_redis.py
python3 ${DIR}/wait_for_es.py

echo 'Creating schemas...'

bash ${DIR}/es_clear.sh

bash ${DIR}/es_schema_movies.sh
bash ${DIR}/es_schema_genres.sh
bash ${DIR}/es_schema_persons.sh

echo 'Upgrading auth database...'
bash ${DIR}/auth_upgade_db.sh

echo 'Running tests...'

pytest --disable-warnings
