FROM airflow_docker_project_common:latest as project_common_pkg




FROM python:3.6-slim-buster AS builder

ENV DEBIAN_FRONTEND noninteractive
ENV AIRFLOW_HOME /tmp/airflow


WORKDIR /app
RUN mkdir -p src/project_complex \
    && touch src/project_complex/__init__.py
COPY setup.* /app/


WORKDIR /project_common_pkg
COPY --from=project_common_pkg /pkg/* /project_common_pkg
RUN pip install /project_common_pkg/*.whl


WORKDIR /app
RUN set -ex \
    && apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y gcc \
    && pip install -e .[dev]


COPY . /app

RUN pytest -vv
RUN pip install --no-deps -e . \
    && python setup.py bdist_wheel




FROM python:3.6-slim-buster

ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

WORKDIR /project_common_pkg
WORKDIR /app
COPY --from=project_common_pkg /pkg/* /project_common_pkg
COPY --from=builder /app/dist/*.whl /app/
COPY bin/* /usr/local/bin/

WORKDIR /



RUN set -ex \
    && apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        bash \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && pip install /project_common_pkg/*.whl \
    && pip install /app/*.whl \
    && mkdir -p /home/airflow \
    && groupadd -g 1000 airflow \
    && useradd -Ms /bin/bash --home /home/airflow -u 1000 -g 1000 airflow \
    && chown airflow:nogroup -R /home/airflow \
    # Prepare DAGs tar:
    && PREFIX="`python3 -c 'import sys; print(sys.prefix.rstrip("/"))'`" \
    && DAGS="$PREFIX/airflow/dags" \
    && cd "$DAGS" \
    && tar cf /dags.tar ./ \
    && rm -Rf /app \
    && rm -rf ~/.cache/pip /tmp/pip-build* \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

USER airflow

ENTRYPOINT ["entrypoint.sh"]
