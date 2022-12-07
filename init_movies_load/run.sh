#!/usr/bin/env bash

export PGPASSWORD=123qwe

docker run -d \
  --name movies-database \
  -p 5432:5432 \
  -v $HOME/postgresql/data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=$PGPASSWORD \
  -e POSTGRES_USER=app \
  -e POSTGRES_DB=movies_database \
  postgres:13

psql --host 127.0.0.1 --username app --dbname movies_database --file movies_database.ddl

python loader/load_data.py
