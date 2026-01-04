ARG PY_VER=3.14
FROM python:${PY_VER}-slim-bookworm

WORKDIR /fsthub

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y hfst gcc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY fsthub ./

ENTRYPOINT ["sh", "-c"]
CMD ["/usr/local/bin/python3 manage.py collectstatic --no-input && \
      /usr/local/bin/uwsgi --http :80 --wsgi-file fsthub/wsgi.py"]
