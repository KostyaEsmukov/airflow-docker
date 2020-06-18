#!/bin/bash

if [ ! -z "$DOCKER_LOGIN" ] && [ -e /var/run/docker.sock ]; then
    echo -n "$DOCKER_LOGIN" | xargs --max-lines=1 docker login
fi


set -euo pipefail

case "$1" in
  scheduler)
    if [ ! -z "${DOCKER_COMPOSE_MODE-}" ]; then
        sleep 5  # let Postgres start
        airflow initdb
        airflow create_user \
            --role Admin \
            --username admin \
            --password admin \
            --email admin@localhost \
            --firstname admin \
            --lastname user
    fi
    if [ -z "${SCHEDULER_CONSUL_LOCK_NAME-}" ]; then
        airflow upgradedb && exec airflow "$@"
    else
        CONSUL_HTTP_TOKEN="$SCHEDULER_CONSUL_HTTP_TOKEN" exec consul lock \
            -name "$SCHEDULER_CONSUL_LOCK_NAME" "$SCHEDULER_CONSUL_LOCK_PREFIX" \
            airflow upgradedb "&&" exec airflow "$@"
    fi
    ;;
  webserver)
    if [ ! -z "${DOCKER_COMPOSE_MODE-}" ]; then
        sleep 10  # let `airflow initdb` finish
    fi
    exec airflow "$@"
    ;;
  worker)
    if [ ! -z "${DOCKER_COMPOSE_MODE-}" ]; then
        sleep 10  # let `airflow initdb` finish
    fi
    exec airflow "$@"
    ;;
  serve_logs)
    if [ ! -z "${DOCKER_COMPOSE_MODE-}" ]; then
        sleep 10  # let `airflow initdb` finish
    fi
    exec airflow "$@"
    ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
    exec "$@"
    ;;
esac
