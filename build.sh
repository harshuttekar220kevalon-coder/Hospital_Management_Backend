#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

pip install -r requirements.txt

# Run migrations to guarantee database integrity on production
python manage.py migrate --noinput

# Collect static files for WhiteNoise
python manage.py collectstatic --no-input
