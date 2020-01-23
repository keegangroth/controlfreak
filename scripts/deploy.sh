#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export ROOT_DIR="${SCRIPT_DIR}/.."
IMAGE='controlfreak:latest'
AWS_ACCOUNT='360384804147'

set -e

echo '+ docker login'
$(aws ecr get-login --no-include-email --region us-west-2 --registry-ids 360384804147)

set -x

docker build -t $IMAGE $ROOT_DIR
docker tag $IMAGE $AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/$IMAGE
docker push $AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com/$IMAGE

aws ecs update-service --cluster controlfreak --service controlfreak-int --force-new-deployment
