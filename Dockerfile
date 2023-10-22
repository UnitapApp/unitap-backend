# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 python:3.10
WORKDIR /code
RUN apt update && apt install gcc
COPY ./requirements/ /code/requirements/
RUN pip install pip --upgrade
#installing requests befor the rest for lnpay compatibility
RUN pip install requests
RUN pip install -r requirements/base.txt
COPY . .
RUN mkdir db
RUN mkdir -p static
RUN mkdir media
RUN chmod +x start_dev.sh

EXPOSE 5678
CMD ./start_dev.sh
