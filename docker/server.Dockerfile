ARG APP_IMAGE=docker.io/kartinka/fsthub-app
ARG FSTHUB_VER

FROM ${APP_IMAGE}:${FSTHUB_VER} AS base-static
COPY ./fsthub/frontend/static /fsthub/frontend/static
RUN /usr/local/bin/python3 manage.py collectstatic --no-input

# no need to minify, nginx compresses static well enough
# FROM tdewolff/minify AS minified-static
# WORKDIR /static
# COPY --from=base-static /static /static
# RUN minify --inplace --all --recursive .

FROM nginx:1.29.4-alpine3.23
COPY ./docker/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=base-static /static /var/www/fsthub/static
