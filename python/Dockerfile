ARG base_image=python:3.7.3-alpine3.9
FROM $base_image

# dcos-cli and lint tooling require this to output cleanly
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8

RUN mkdir /dcos-service-diagnostics-dist

COPY ./base_tech_bundle /dcos-service-diagnostics-dist/base_tech_bundle
COPY ./dcos-commons/testing /dcos-service-diagnostics-dist/dcos-commons/testing
COPY *.py *.sh Pipfile Pipfile.lock /dcos-service-diagnostics-dist/

RUN ls -la /dcos-service-diagnostics-dist

RUN apk add --no-cache --virtual=.build-dependencies \
        build-base    \
        openssl-dev   \
        libffi-dev && \
        pip install pipenv && \
        cd /dcos-service-diagnostics-dist/ && \
        pipenv install --system && \
    apk del .build-dependencies
