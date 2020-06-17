FROM python:3.6-slim-buster AS builder

ENV DEBIAN_FRONTEND noninteractive
ENV AIRFLOW_HOME /tmp/airflow

WORKDIR /app
RUN mkdir -p src/project_common \
    && touch src/project_common/__init__.py
COPY setup.* /app/

RUN set -ex \
    && apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y gcc \
    && pip install -e .[dev]


COPY . /app

RUN pytest -vv
RUN pip install --no-deps -e . \
    && python setup.py bdist_wheel




FROM busybox

WORKDIR /pkg
COPY --from=builder /app/dist/*.whl /pkg/
