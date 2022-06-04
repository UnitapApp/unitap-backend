# syntax=docker/dockerfile:1
FROM python:3.8.10
WORKDIR /code
COPY requirements.txt /code/
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
COPY . .
RUN mkdir db
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 5678
CMD uwsgi --socket 0.0.0.0:5678 --protocol=http -w brightIDfaucet.wsgi