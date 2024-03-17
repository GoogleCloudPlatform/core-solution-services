#!/bin/bash
# Script to run unit tests in a component

# Get the absolute path to the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Set BASE_DIR to the directory one level up
BASE_DIR="$(dirname "$SCRIPT_DIR")"

PYTEST_ADDOPTS="--cache-clear --cov . " PYTHONPATH=$BASE_DIR/components/common/src python -m pytest
