#
# thanks to: https://github.com/binxio/aws-lambda-git
#
.PHONY: deploy dev build start-api dependencies generate-git-zip layers layer-git layer-python sam-deploy swagger-ui



deploy: build sam-deploy swagger-ui

dev: build start-api


# publish
sam-deploy:
	sam deploy

swagger-ui:
	aws s3 cp $(PWD)/openapi.json s3://whattheversion.hutter.cloud/openapi.json
	aws s3 sync $(PWD)/swagger-ui/ s3://whattheversion.hutter.cloud/


# build with sam
build: layers
	sam build --use-container 

start-api:
	sam local start-api --warm-containers EAGER
# install dependencies and copyh layer code

# create layer for git binary, the binary will be available in /opt/git/bin, the libs in /opt/git/lib.

layers: layer-git layer-python

layer-git:
	-rm -rf layers/git
	mkdir -p layers/git/git
	unzip helper/git-cli/git-cli-amd64.zip -d layers/git/git/

layer-python:
	-rm -rf layers/whattheversion
	mkdir -p layers/whattheversion/python
	cp -a src/whattheversion layers/whattheversion/python/whattheversion
	venv/bin/pip install -r layers/whattheversion/python/whattheversion/requirements.txt -t layers/whattheversion/python/

generate-git-zip:
	cd helper/git-cli ; bash git-cli-amd64.sh