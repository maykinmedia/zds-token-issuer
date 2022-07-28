# This is a multi-stage build file, which means a stage is used to build
# the backend (dependencies), the frontend stack and a final production
# stage re-using assets from the build stages. This keeps the final production
# image minimal in size.

# Stage 1 - Backend build environment
# includes compilers and build tooling to create the environment

FROM python:3.9-alpine AS backend-build

RUN apk --no-cache add \
    gcc \
    musl-dev \
    pcre-dev \
    linux-headers \
    postgresql-dev

WORKDIR /app

# Ensure we use the latest version of pip
RUN pip install pip setuptools -U

COPY ./requirements /app/requirements
RUN pip install -r requirements/production.txt


# Stage 2 - Install frontend deps and build assets
FROM mhart/alpine-node:12 AS frontend-build

WORKDIR /app

# copy configuration/build files
COPY ./*.json /app/
RUN npm install

# copy (scss/js) source code
COPY ./src/token_issuer/sass /app/src/token_issuer/sass/
COPY ./src/token_issuer/js /app/src/token_issuer/js/

# build frontend
RUN npm run build


# Stage 3 - Build docker image suitable for production
FROM python:3.9-alpine

RUN apk --no-cache add \
    ca-certificates \
    mailcap \
    musl \
    pcre \
    postgresql

WORKDIR /app
COPY ./bin/docker_start.sh /start.sh
RUN mkdir /app/log

# copy backend build deps
COPY --from=backend-build /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=backend-build /usr/local/bin/uwsgi /usr/local/bin/uwsgi

# copy build statics
COPY --from=frontend-build /app/src/token_issuer/static/bundles /app/src/token_issuer/static/bundles
COPY --from=frontend-build /app/src/token_issuer/static/fonts /app/src/token_issuer/static/fonts

# copy source code
COPY ./src /app/src

ENV DJANGO_SETTINGS_MODULE=token_issuer.conf.docker

ARG SECRET_KEY=dummy

# Run collectstatic, so the result is already included in the image
RUN python src/manage.py collectstatic --noinput

EXPOSE 8000
CMD ["/start.sh"]
