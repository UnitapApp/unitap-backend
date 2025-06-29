worker: celery -A brightIDfaucet worker -B
beat: celery -A brightIDfaucet beat -l INFO
web: gunicorn brightIDfaucet.wsgi --workers 2 --threads 2
