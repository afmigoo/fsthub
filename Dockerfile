FROM python:3.13-slim-bookworm

WORKDIR /fsthub

RUN apt update -y && apt upgrade -y
RUN apt install -y hfst gcc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fsthub ./

CMD ["/usr/local/bin/uwsgi", "--http", ":8000", \
                             "--wsgi-file", "fsthub/wsgi.py"]