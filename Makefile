#
# thanks to: https://github.com/binxio/aws-lambda-git
#

deploy: build sam-deploy swagger-ui

dev: build dynamodb start-api


# publish
sam-deploy:
	sam deploy

swagger-ui: openapi.json
	aws s3 cp $(PWD)/openapi.json s3://whattheversion.hutter.cloud/openapi.json
	aws s3 sync $(PWD)/swagger-ui/ s3://whattheversion.hutter.cloud/


# build with sam
build: layers
	sam build --use-container 

#
# local dev
#
dynamodb:
	-docker-compose up -d
	-AWS_ACCESS_KEY_ID=local AWS_SECRET_ACCESS_KEY=local \
	    aws dynamodb --region eu-central-1 create-table \
		--table-name whattheversion \
		--attribute-definitions AttributeName=PK,AttributeType=S \
		--key-schema AttributeName=PK,KeyType=HASH \
		--billing-mode PAY_PER_REQUEST \
		--endpoint-url http://localhost:8000

start-api:
	sam local start-api --warm-containers EAGER --env-vars $(PWD)/helper/dev/env-vars.json

#
# layers
#
layers: layer-git layer-python layer-helm-to-json

layer-helm-to-json: helper/helm-to-json/helm-to-json.linux
	-rm -rf layers/helm-to-json
	# two times the directory is no accident
	# this puts the bin into '/opt/helm-to-json' in the layer which can be added to the path
	mkdir -p layers/helm-to-json/helm-to-json/
	cp helper/helm-to-json/helm-to-json.linux layers/helm-to-json/helm-to-json/helm-to-json

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

generate-helm-to-json:
	cd helper/helm-to-json ; bash helm-to-json.sh