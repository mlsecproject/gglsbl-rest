#!/usr/bin/env bash
#
# Script to deploy gglsbl-rest to an AWS ECS cluster repository and service using "ecs-deploy".
#
# Please provide the following environment variables:
#
# REPO: the part of the ECS full repository URI before the slash
# SERVICE: the part of the ECS full repository URI after the slash
# CLUSTER: the name of the ECS cluster
# PROFILE: the AWS CLI profile to use (in ~/.aws/credentials), if missing will use "default"
#

if [ -z "$PROFILE" ]; then
    PROFILE=default
fi

if [ -z "$SERVICE" ] || [ -z "$REPO" ] || [ -z "$CLUSTER" ]; then
    echo Please define SERVICE, REPO and CLUSTER correctly
else
    set -e
    TAG=`git rev-parse --verify HEAD`
    IMAGE=$REPO/$SERVICE:${TAG}
    echo Building $IMAGE ...
    docker build -t $IMAGE .
    echo Pushing $IMAGE ...
    eval $(aws ecr get-login --no-include-email --profile ${PROFILE})
    docker push $IMAGE
    echo Deploy $IMAGE to profile $PROFILE, cluster $CLUSTER and service $SERVICE ...
    deploy/ecs-deploy -p ${PROFILE} -c ${CLUSTER} -n $SERVICE -i $IMAGE -m 50
    echo Deployed!
    docker logout
    docker rmi $IMAGE
fi
