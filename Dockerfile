FROM python:3.13-slim-bookworm

WORKDIR /fsthub

RUN apt update -y && apt upgrade -y
RUN apt install -y hfst
RUN apt install -y gcc

COPY fsthub ./
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["/usr/local/bin/uwsgi", "--http", ":8000", \
                             "--wsgi-file", "fsthub/wsgi.py"]