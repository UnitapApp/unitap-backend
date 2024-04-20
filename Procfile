worker: celery -A brightIDfaucet worker -B
release: python manage.py migrate
web: gunicorn brightIDfaucet.wsgi --workers 4 --threads 2
