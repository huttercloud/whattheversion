#!/bin/bash

#
# build helper binary for helm lambda
# as the pyyaml baseloader takes 20+ seconds to parse a bigger helm chart!
#

docker rm -f helm-to-json-builder
docker build -t helm-to-json-builder -f Dockerfile .
docker run -d --name helm-to-json-builder helm-to-json-builder
docker cp helm-to-json-builder:/app/helm-to-json.linux ./
docker cp helm-to-json-builder:/app/helm-to-json.macos ./
docker rm -f helm-to-json-builder
