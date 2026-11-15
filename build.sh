#!/usr/bin/env bash
# Render build script for CloudPad Django app (run from repo root)
set -o errexit  # Exit on any error

# Install Python dependencies
pip install -r requirements.txt

# Collect static files (WhiteNoise will serve them)
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate
