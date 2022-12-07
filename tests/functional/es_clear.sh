curl \
    -XDELETE "http://${ELASTIC_HOST}:${ELASTIC_PORT}/_all?pretty" \
    -H 'Content-Type: application/json' \
    -u ${ELASTIC_USERNAME}:${ELASTIC_PASSWORD} \
    --silent
