#!/usr/bin/env bash

set -e

SCRIPT_DIR="$( cd "$( dirname "$( readlink -f "${BASH_SOURCE[0]}" )" )" && pwd )"

cd "$SCRIPT_DIR"

if [ ! -d venv ]; then
    python3 -m venv venv
fi

. venv/bin/activate &&
    pip install -r requirements.txt &&
    alembic upgrade head &&
    ./app.py $*
