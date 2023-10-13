# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.10
WORKDIR /code
COPY requirements.txt /code/
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
COPY . .
RUN mkdir db
RUN mkdir -p static
RUN mkdir media
RUN chmod +x start_dev.sh

EXPOSE 5678
CMD ./start_dev.sh