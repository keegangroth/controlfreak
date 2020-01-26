#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export ROOT_DIR="${SCRIPT_DIR}/.."
export IMAGE='controlfreak'
export GIT_SHA=$(git rev-parse --short HEAD)
export AWS_ACCOUNT='360384804147'
export ECR=$AWS_ACCOUNT.dkr.ecr.us-west-2.amazonaws.com
