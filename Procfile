worker: celery -A brightIDfaucet worker -B
release: python manage.py migrate
web: gunicorn brightIDfaucet.wsgi
web2: gunicorn brightIDfaucet.wsgi
