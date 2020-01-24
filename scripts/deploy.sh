#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export ROOT_DIR="${SCRIPT_DIR}/.."
IMAGE='controlfreak'
AWS_ACCOUNT='360384804147'
GIT_SHA=$(git rev-parse --short HEAD)

set -e

echo '+ docker login'
$(aws ecr get-login --no-include-email --region us-west-2 --registry-ids $AWS_ACCOUNT)

set -x

docker build -t $IMAGE:latest $ROOT_DIR
docker tag $IMAGE:latest $AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/$IMAGE:${GIT_SHA}
docker tag $IMAGE:latest $AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/$IMAGE:latest
docker push $AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/$IMAGE:latest

aws ecs update-service --cluster controlfreak --service controlfreak-int --force-new-deployment
