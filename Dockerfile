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
# Don't copy source code here, as changes will bust the cache for everyting
# below


# Stage 2 - build frontend
FROM mhart/alpine-node:16 AS frontend-build

WORKDIR /app

# copy configuration/build files
COPY ./*.json /app/
RUN npm install

COPY ./*.js ./.babelrc /app/
COPY ./build /app/build/

# copy (scss/js) source code
COPY ./src/token_issuer/sass /app/src/token_issuer/sass/
COPY ./src/token_issuer/js /app/src/token_issuer/js/
COPY ./src/token_issuer/static/fonts /app/src/token_issuer/static/fonts/

# build frontend
RUN npm run build


# Stage 3 - Prepare CI tests image
FROM backend-build AS jenkins

RUN apk --no-cache add \
    postgresql-client

COPY --from=backend-build /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=backend-build /app/requirements /app/requirements

RUN pip install -r requirements/ci.txt --exists-action=s

# Stage 3.2 - Set up testing config
COPY ./setup.cfg /app/setup.cfg
COPY ./bin/runtests.sh /runtests.sh

# Stage 3.3 - Copy source code
COPY --from=frontend-build /app/src/token_issuer/static/bundles /app/src/token_issuer/static/bundles
COPY --from=frontend-build /app/src/token_issuer/static/fonts /app/src/token_issuer/static/fonts
COPY ./src /app/src
ARG COMMIT_HASH
ENV GIT_SHA=${COMMIT_HASH}

RUN mkdir /app/log && rm /app/src/token_issuer/conf/ci.py
CMD ["/runtests.sh"]


# Stage 4 - Build docker image suitable for production
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
