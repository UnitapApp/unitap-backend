#!/bin/bash
python manage.py collectstatic --noinput
# python manage.py migrate
python manage.py runserver 0.0.0.0:5678
# celery -A brightIDfaucet worker -B