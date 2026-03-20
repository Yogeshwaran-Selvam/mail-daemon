#!/usr/bin/env bash
# exit on error
set -o errexit

# Install your dependencies
pip install -r requirements.txt

# Tell Django to gather all static files into the 'staticfiles' folder
python manage.py collectstatic --no-input

# Run your database migrations
python manage.py migrate