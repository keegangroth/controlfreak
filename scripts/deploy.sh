#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="${SCRIPT_DIR}/.."
IMAGE='controlfreak'
AWS_ACCOUNT='360384804147'
GIT_SHA=$(git rev-parse --short HEAD)
ECR=$AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com

set -e

echo '+ docker login'
$(aws ecr get-login --no-include-email --region us-west-2 --registry-ids $AWS_ACCOUNT)

set -x

docker build -t $IMAGE:latest -t $ECR/$IMAGE:$GIT_SHA -t $ECR/$IMAGE:latest $ROOT_DIR
for TAG in latest $GIT_SHA; do
    docker push $ECR/$IMAGE:$TAG
done

aws ecs update-service --cluster controlfreak --service controlfreak-int --force-new-deployment
