worker: celery -A brightIDfaucet worker -B
beat: celery -A brightIDfaucet beat -l INFO
release: python manage.py migrate
web: gunicorn brightIDfaucet.wsgi --workers 2 --threads 2
