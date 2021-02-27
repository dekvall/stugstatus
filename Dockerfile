FROM python:3.9-slim-buster

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt


COPY . /stugstatus
WORKDIR /stugstatus

EXPOSE 5000

CMD gunicorn --worker-class gevent --workers 1 --bind 0.0.0.0:5000 wsgi:app --max-requests 100 --timeout 5 --keep-alive 5 --log-level info