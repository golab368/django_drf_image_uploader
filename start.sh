#!/bin/sh

celery --app api.celery worker --loglevel=INFO &
python manage.py runserver 0.0.0.0:8000
