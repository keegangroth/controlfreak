#!/usr/bin/env bash

. $(dirname $0)/__init__.sh

set -e

$(dirname $0)/build.sh

set +x
echo '+ docker login'
$(aws ecr get-login --no-include-email --region us-west-2 --registry-ids $AWS_ACCOUNT)
set -x

for TAG in latest $GIT_SHA; do
    docker push $ECR/$IMAGE:$TAG
done

aws ecs update-service --cluster controlfreak --service controlfreak-int --force-new-deployment
