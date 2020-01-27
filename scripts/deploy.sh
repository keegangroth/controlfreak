#!/usr/bin/env bash

. $(dirname $0)/__init__.sh

set -e

$(dirname $0)/build.sh

if [[ -n $(git status --porcelain --untracked-files=no) ]]; then
    git diff --stat
    echo "Do not deploy uncommitted changes!"
    exit 1
fi

set +x
echo '+ docker login'
$(aws ecr get-login --no-include-email --region us-west-2 --registry-ids $AWS_ACCOUNT)
set -x

for TAG in latest $GIT_SHA; do
    docker push $ECR/$IMAGE:$TAG
done

# Run any DB migrations (async)
aws ecs run-task --cli-input-json file://$ROOT_DIR/scripts/infrastructure/migration_task.json
# Force the cluster to run the new code
aws ecs update-service --cluster controlfreak --service controlfreak-int --force-new-deployment
