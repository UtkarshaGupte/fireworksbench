#!/bin/bash

# dockerentrypoint.sh

set -e  # Exit immediately if a command exits with a non-zero status.
set -u  # Treat unset variables as an error and exit immediately.

exec poetry run python main.py "$@"