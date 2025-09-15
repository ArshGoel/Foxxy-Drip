#!/usr/bin/env sh
set -e

echo "Waiting for database..."
until python manage.py showmigrations > /dev/null 2>&1; do
  sleep 2
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn Foxxy_Drip.wsgi:application \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers ${GUNICORN_WORKERS:-4} \
  --threads ${GUNICORN_THREADS:-2} \
  --timeout ${GUNICORN_TIMEOUT:-30} \
  --log-level info \
  --access-logfile '-' \
  --error-logfile '-'
