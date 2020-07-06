default: build

DOCKER_BUILDX_ARGS ?=
DOCKER_IMAGE ?= mesaguy/galaxy-exporter
DOCKER_PLATFORMS = linux/amd64,linux/arm64,linux/arm/v6,linux/arm/v7,linux/ppc64le,linux/s390x,linux/386
VERSION = `python3 -c 'import galaxy_exporter; print(galaxy_exporter.__version__)'`

.PHONY: all build clean

build:
	docker build --pull \
		--tag ${DOCKER_IMAGE}:latest \
		--tag ${DOCKER_IMAGE}:${VERSION} \
		.

push:
	docker push \
		${DOCKER_IMAGE}:${VERSION}
	docker push \
		${DOCKER_IMAGE}:latest


build_multiarch:
	docker buildx build --pull --platform ${DOCKER_PLATFORMS} \
		--tag ${DOCKER_IMAGE}:${VERSION} \
		--tag ${DOCKER_IMAGE}:latest \
        ${DOCKER_BUILDX_ARGS} .

push_multiarch:
	docker buildx build --pull --platform ${DOCKER_PLATFORMS} \
		--tag ${DOCKER_IMAGE}:${VERSION} \
		--tag ${DOCKER_IMAGE}:latest \
        --push \
        ${DOCKER_BUILDX_ARGS} .
