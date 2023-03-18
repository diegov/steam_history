#!/usr/bin/env bash

set -eo pipefail

echo "Running Mypy" >&2
# TODO: Add --strict
mypy --warn-unused-configs --warn-return-any *.py
echo ""

echo "Running Pyright" >&2
pyright --lib *.py
echo ""
