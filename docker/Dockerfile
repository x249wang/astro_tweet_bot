FROM python:3.7-slim

WORKDIR /
COPY app.py /

RUN apt-get -y update

RUN pip install --no-cache-dir gunicorn Flask sqlalchemy tweepy pg8000

CMD exec gunicorn --bind :$PORT --workers 1 --timeout 500 app:app
