#
# thanks to: https://github.com/binxio/aws-lambda-git
#

deploy: build-remote
	sam deploy
dev: build-local start-api
build-remote: dependencies git-remote build
build-local: dependencies git-remote build

# build with sma
build:
	sam build --use-container 

start-api:
	sam local start-api --warm-containers EAGER
# install dependencies and copyh layer code
dependencies: dependencies/python/requirements.txt 
	cp -a src/whattheversion dependencies/python/whattheversion
	venv/bin/pip install -r dependencies/python/requirements.txt -t dependencies/python/

# setup git bin and libs for deployment
# the referenced zip was created on a linux amd64 box to ensure compatibility with
# the lambda execution environment
git: helper/build/git-cli-amd64.zip
	-rm -rf "$(PWD)/src/git/bin"
	-rm -rf "$(PWD)/src/git/lib"
	unzip helper/build/git-cli-amd64.zip -d "$(PWD)/src/git/"

generate-git-zip:
	cd helper/build ; bash git-cli-amd64.sh