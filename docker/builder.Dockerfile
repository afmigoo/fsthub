ARG PY_VER=3.14
FROM python:${PY_VER}-slim-trixie

RUN apt-get update -y && apt-get upgrade -y \
      && apt-get install -y make hfst lexd \
      && apt-get clean

WORKDIR /build
ENTRYPOINT ["sh", "-c"]
CMD ["make"]
