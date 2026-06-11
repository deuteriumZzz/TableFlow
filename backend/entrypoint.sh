#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting daphne (ASGI)..."
exec daphne -b 0.0.0.0 -p 8000 config.routing:application
