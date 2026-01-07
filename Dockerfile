ARG PY_VER=3.14
# BASE
FROM python:${PY_VER}-slim-trixie AS base

RUN apt-get update -y && apt-get upgrade -y \
      && apt-get install -y make hfst \
      && apt-get clean
ENTRYPOINT ["sh", "-c"]

# APP
FROM base AS app

WORKDIR /fsthub
COPY requirements.txt .
RUN apt-get install -y gcc \
      && pip install -r requirements.txt \
      && apt-get purge -y gcc \
      && apt-get autoremove -y
COPY fsthub ./
CMD ["/usr/local/bin/python3 manage.py collectstatic --no-input && \
      /usr/local/bin/python3 manage.py migrate && \
      /usr/local/bin/python3 manage.py projectsautoinit && \
      /usr/local/bin/uwsgi --http :80 --wsgi-file fsthub/wsgi.py"]

# BUILDER
FROM base AS builder

WORKDIR /build
RUN apt-get install -y lexd \
      && apt-get clean
CMD ["make"]
