#!/bin/bash

#
# execute this script on an amd64 machine to create a lambda compatible git bin and libs
# 

docker rm -f git-builder
docker build -t git-container -f Dockerfile.git-cli .
docker run -d --name git-builder git-container
docker cp git-builder:/tmp/libraries.zip git-cli-amd64.zip
docker rm -f git-builder
