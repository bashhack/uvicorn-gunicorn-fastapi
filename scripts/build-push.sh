#!/usr/bin/env bash

set -ex

use_tag="bashhack/uvicorn-gunicorn-fastapi:$NAME"
use_dated_tag="${use_tag}-$(date -I)"

docker build -t "$use_tag" "$BUILD_PATH"

docker tag "$use_tag" "$use_dated_tag"

docker push "$use_tag"
docker push "$use_dated_tag"