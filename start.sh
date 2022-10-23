#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate
uwsgi --socket 0.0.0.0:5678 --protocol=http -w brightIDfaucet.wsgi