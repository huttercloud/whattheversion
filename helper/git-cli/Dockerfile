#
# install git client for lambda function
# thanks to: https://github.com/binxio/aws-lambda-git
#

FROM  --platform=linux/amd64 public.ecr.aws/lambda/python:3.9

RUN mkdir -p /var/task/{bin,lib}
RUN yum install -y git zip

WORKDIR /var/task

RUN cp /usr/bin/git /var/task/bin \
    && cp /usr/libexec/git-core/git-ls-remote /var/task/bin \
    && cp /usr/libexec/git-core/git-remote-https /var/task/bin \
    && cp /usr/libexec/git-core/git-remote-http /var/task/bin

RUN ldd /usr/bin/git | awk 'NF == 4 { system("cp " $3 " /var/task/lib/") }' \
    && ldd /usr/libexec/git-core/git-ls-remote | awk 'NF == 4 { system("cp " $3 " /var/task/lib/") }' \
    && ldd /usr/libexec/git-core/git-remote-https | awk 'NF == 4 { system("cp " $3 " /var/task/lib/") }' \
    && ldd /usr/libexec/git-core/git-remote-http | awk 'NF == 4 { system("cp " $3 " /var/task/lib/") }'

RUN zip -r9 /tmp/libraries.zip *