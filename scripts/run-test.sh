#!/usr/bin/env bash

# Resolve the project root relative to this script's own location,
# so run-test.sh works no matter which directory it's invoked from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

TESTING=true "$PROJECT_ROOT/python3-virtualenv/bin/python" -m unittest discover -v "$PROJECT_ROOT/tests/"