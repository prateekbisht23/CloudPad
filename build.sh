#!/usr/bin/env bash
# Render build script for CloudPad Django app
set -o errexit  # Exit on any error

# Navigate to Django project directory
cd CloudPad

# Install Python dependencies
pip install -r requirements.txt

# Collect static files (WhiteNoise will serve them)
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate
