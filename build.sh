#!/bin/bash

# Exit on error
set -o errexit

# Install dependencies
python3 -m pip install -r requirements.txt

# Create staticfiles directory if it doesn't exist
mkdir -p staticfiles

# Collect static files
python3 manage.py collectstatic --noinput

# Run migrations
python3 manage.py migrate --noinput

# Create superuser if credentials provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python3 create_superuser.py
fi
