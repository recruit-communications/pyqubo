#!/usr/bin/env bash
set -eu

DOCKER_IMAGE=${DOCKER_IMAGE:-'pyqubo/manylinux_cmake_wo_ssh:latest'}

repo_dir=$(cd $(dirname $0); pwd)

docker run \
  -v $repo_dir:/root/ \
  -w /root \
  --rm \
  ${DOCKER_IMAGE} \
  bash ./test_run.sh
