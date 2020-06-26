default: build

DOCKER_IMAGE ?= mesaguy/galaxy-exporter
PYTHON_VERSION ?= python:3.8.3-alpine3.12
DOCKER_TARGET_REGISTRY ?=
BUILD_DATE = `date --utc +%Y%m%d`
VERSION = `python -c 'import galaxy_exporter; print(galaxy_exporter.__version__)'`

.PHONY: all build clean

build:
	docker build --pull \
		--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
		--pull \
		--tag ${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:latest \
		--tag ${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:${BUILD_DATE} \
		--tag ${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:${VERSION} \
		.

push:
	docker push \
		${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:latest
	docker push \
		${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:${BUILD_DATE}
	docker push \
		${DOCKER_TARGET_REGISTRY}${DOCKER_IMAGE}:${VERSION}
