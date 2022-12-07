#!/bin/bash
echo "Starting service..."
/usr/sbin/nginx
gunicorn --bind=0.0.0.0:8000 config.wsgi
