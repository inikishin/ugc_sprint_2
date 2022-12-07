#!/usr/bin/env bash

export PGPASSWORD=123qwe

docker run -d \
  --name auth-database \
  -p 5431:5432 \
  -v $HOME/postgresql/auth_data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=$PGPASSWORD \
  -e POSTGRES_USER=app \
  -e POSTGRES_DB=auth_database \
  postgres:13
