ARG FSTHUB_VER=latest

FROM docker.io/kartinka/fsthub-app:${FSTHUB_VER} AS base-static
COPY fsthub/frontend/static ./frontend/static
RUN /usr/local/bin/python3 manage.py collectstatic --no-input

FROM nginx:1.29.4-alpine3.23
COPY ./docker/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=base-static /static /var/www/fsthub/static
