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

# Create default users (admin/admin and user/user)
echo "Creating default users..."
python3 create_superuser.py
