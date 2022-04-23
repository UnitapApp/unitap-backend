# syntax=docker/dockerfile:1
FROM python:3.8.10
WORKDIR /code
COPY requirements.txt /code/
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 5678
CMD daphne -b 0.0.0.0 -p 5678 brightIDfaucet.asgi:application