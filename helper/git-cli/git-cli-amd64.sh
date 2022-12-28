#!/bin/bash

#
# create zip containing git binaries and libs for lambda layer
# 

docker rm -f git-builder
docker build -t git-builder -f Dockerfile .
docker run -d --name git-builder git-builder
docker cp git-builder:/tmp/libraries.zip git-cli-amd64.zip
docker rm -f git-builder
