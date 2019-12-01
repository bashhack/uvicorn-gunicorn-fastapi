#!/usr/bin/env bash
set -ex

use_tag="bashhack/uvicorn-gunicorn-fastapi:$NAME"

docker build -t "$use_tag" "$BUILD_PATH"
pytest