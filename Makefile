default: build

BUILD_DATE = `date --utc +%Y%m%d`
DOCKER_BUILDX_ARGS ?=
DOCKER_IMAGE ?= mesaguy/galaxy-exporter
DOCKER_PLATFORMS = linux/amd64,linux/arm64,linux/arm/v6,linux/arm/v7,linux/ppc64le,linux/s390x,linux/386
PYTHON_VERSION ?= python:3.8-alpine
VERSION = `python3 -c 'import galaxy_exporter; print(galaxy_exporter.__version__)'`

.PHONY: all build clean

build:
	docker build --pull \
		--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
		--tag ${DOCKER_IMAGE}:latest \
		--tag ${DOCKER_IMAGE}:${BUILD_DATE} \
		--tag ${DOCKER_IMAGE}:${VERSION} \
		.

push:
	docker push \
		${DOCKER_IMAGE}:latest
	docker push \
		${DOCKER_IMAGE}:${BUILD_DATE}
	docker push \
		${DOCKER_IMAGE}:${VERSION}


build_multiarch:
	docker buildx build --pull --platform ${DOCKER_PLATFORMS} \
		--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
		--tag ${DOCKER_IMAGE}:latest \
		--tag ${DOCKER_IMAGE}:${BUILD_DATE} \
		--tag ${DOCKER_IMAGE}:${VERSION} \
        ${DOCKER_BUILDX_ARGS} .

push_multiarch:
	docker buildx build --pull --platform ${DOCKER_PLATFORMS} \
		--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
		--tag ${DOCKER_IMAGE}:latest \
		--tag ${DOCKER_IMAGE}:${BUILD_DATE} \
		--tag ${DOCKER_IMAGE}:${VERSION} \
        --push \
        ${DOCKER_BUILDX_ARGS} .
