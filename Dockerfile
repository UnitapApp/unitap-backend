# syntax=docker/dockerfile:1
FROM python:3.8.10
WORKDIR /code
COPY requirements.txt /code/
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
COPY . .
RUN mkdir db
RUN mkdir static
RUN mkdir media
RUN chmod +x start.sh

EXPOSE 5678
CMD ./start.sh