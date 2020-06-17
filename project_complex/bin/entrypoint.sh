#!/bin/bash

if which "$1" >/dev/null 2>&1; then
    exec "$@"
else
    exec python3 -u -m "$@"
fi
