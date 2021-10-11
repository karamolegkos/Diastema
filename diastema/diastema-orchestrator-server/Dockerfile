# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN pip3 install flask
RUN pip3 install requests
RUN pip3 install minio
RUN pip3 install pymongo

COPY . .

CMD [ "flask", "run", "--host=0.0.0.0"]