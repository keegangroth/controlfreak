#!/usr/bin/env bash

. $(dirname $0)/__init__.sh

set -ex

docker build -t $IMAGE:latest -t $ECR/$IMAGE:$GIT_SHA -t $ECR/$IMAGE:latest $ROOT_DIR
docker run $IMAGE:latest coverage run manage.py test && coverage report
docker run $IMAGE:latest pylint server
