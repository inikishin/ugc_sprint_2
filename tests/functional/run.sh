#!/usr/bin/env bash

SCRIPT_DIR=`dirname "$0"`

cd ${SCRIPT_DIR};

docker-compose \
    -f docker-compose.yml up --build \
    --abort-on-container-exit \
    --exit-code-from tests

docker-compose rm -f -v
