#
# thanks to: https://github.com/binxio/aws-lambda-git
#

deploy: build sam-deploy swagger-ui

dev: build localstack dynamodb eventbus start-api


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
localstack:
	docker-compose up -d

dynamodb:
	@sleep 3
	-AWS_ACCESS_KEY_ID=local AWS_SECRET_ACCESS_KEY=local \
	    aws dynamodb --region eu-central-1 create-table \
			--table-name whattheversion \
			--attribute-definitions AttributeName=PK,AttributeType=S \
			--key-schema AttributeName=PK,KeyType=HASH \
			--billing-mode PAY_PER_REQUEST \
			--endpoint-url http://localhost:4566 >/dev/null

eventbus:
	@sleep 3
	-AWS_ACCESS_KEY_ID=local AWS_SECRET_ACCESS_KEY=local \
		aws events --region eu-central-1 put-rule \
			--name "DockerEvent" \
			--event-pattern "{\"source\":[\"cloud.hutter.whattheversion\"],\"detail-type\":[\"Create or Update DynamoDB versions entry\"],\"detail\":{\"source\":[\"docker\"]}}" \
			--endpoint-url http://localhost:4566
	-AWS_ACCESS_KEY_ID=local AWS_SECRET_ACCESS_KEY=local \
		aws events --region eu-central-1 put-rule \
			--name "GitEvent" \
			--event-pattern "{\"source\":[\"cloud.hutter.whattheversion\"],\"detail-type\":[\"Create or Update DynamoDB versions entry\"],\"detail\":{\"source\":[\"git\"]}}" \
			--endpoint-url http://localhost:4566
	-AWS_ACCESS_KEY_ID=local AWS_SECRET_ACCESS_KEY=local \
		aws events --region eu-central-1 put-rule \
			--name "HelmEvent" \
			--event-pattern "{\"source\":[\"cloud.hutter.whattheversion\"],\"detail-type\":[\"Create or Update DynamoDB versions entry\"],\"detail\":{\"source\":[\"helm\"]}}" \
			--endpoint-url http://localhost:4566

start-api:
	sam local start-api --warm-containers EAGER --env-vars $(PWD)/helper/dev/env-vars.json --parameter-overrides ParameterKey=Environment,ParameterValue=LOCAL

#
# layers
#
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
