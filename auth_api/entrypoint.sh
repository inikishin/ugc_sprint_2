#!/bin/bash
echo "Upgrading Database..."
alembic upgrade head

echo "Starting service..."
gunicorn --bind 0.0.0.0:5000 \
          -k gevent \
          --log-level=debug \
          --access-logfile=/data/log/access_print.log \
          --error-logfile=/data/log/error_print.log \
          wsgi_app:app
