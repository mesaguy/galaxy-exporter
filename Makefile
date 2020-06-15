default: build

DOCKER_IMAGE ?= mesaguy/galaxy_dl_count
PYTHON_VERSION ?= python:3.8.3-alpine3.11
DOCKER_TARGET_REGISTRY ?=
BUILD_DATE = `date --utc +%Y%m%d`

build:
	docker build --pull \
		--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
		--build-arg SOURCE_COMMIT=`git rev-parse --short HEAD` \
		--pull \
		--tag ${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:latest \
		--tag ${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:${BUILD_DATE} \
		.

push:
	docker build --pull \
		--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
		--build-arg SOURCE_COMMIT=`git rev-parse --short HEAD` \
		--tag ${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:latest \
		--tag ${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:${BUILD_DATE} \
		--pull \
		--push \
		.
