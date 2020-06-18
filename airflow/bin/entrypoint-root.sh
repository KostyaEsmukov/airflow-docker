#!/bin/bash

if [ -e /var/run/docker.sock ]; then
    # Add `docker` group to the `airflow` user:
    set -e
    if [ ! -z "${DOCKER_COMPOSE_MODE-}" ]; then
        # A hack for macos, where the docker.sock is owned
        # by `root` instead of `docker`:
        chgrp 12312 /var/run/docker.sock || true
    fi
    _GROUP_GID="`stat --format "%g" /var/run/docker.sock`"
    groupdel -f docker || true  # missing group is okay
    # Ensure that this GID is not taken:
    if getent group "$_GROUP_GID"; then
        echo "GID $_GROUP_GID is taken. It must be free to avoid" \
            "conflict with a system's 'docker' group's GID"
        exit 1
    fi
    groupadd docker --gid "$_GROUP_GID"
    gpasswd -a airflow docker
    set +e
fi

exec gosu airflow entrypoint-airflow.sh "$@"
