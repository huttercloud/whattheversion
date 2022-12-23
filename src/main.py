#!/usr/bin/env python3

"""
    receives a post payload (lambda invocation url
    checks the given helm repo, docker registry or git repo (public repos only)
    and tries to return the most up to date version.

    the lambda function expects a json formated body
"""

import sys
import json
import logging
import requests

from utils.versions import VersionsRequest


def handler(event, context):
    """
        lambda handler
    """


    try:
        request = VersionsRequest(**json.loads(event['body']))

        for g in request.git:
            print(f'{g.repository}: {g.get_latest_tag()}')

        for d in request.docker:
            print(f'{d.repository}: {d.get_latest_tag()}')

        print('yarp')

    except Exception as e:
        logging.error(e)
        sys.exit(1)



if __name__ == '__main__':
    event = dict(
        body = json.dumps(

            dict(
                git=[
                    dict(
                        repository='github.com/clinton-hall/nzbToMedia.git',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    )
                ],
                docker=[
                    # dict(
                    #     repository='registry.hub.docker.com/linuxserver/sonarr',
                    #     regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
                    # ),
                    dict(
                        # https://quay.io/api/v1/repository/oauth2-proxy/oauth2-proxy/tag/
                        repository='quay.io/oauth2-proxy/oauth2-proxy',
                        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    # dict(
                    #     repository='registry.hub.docker.com/filebrowser/filebrowser',
                    #     regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$'
                    # ),
                    # dict(
                    #     repository='registry.hub.docker.com/sebastianhutter/sabnzbd',
                    #     regexp='^.{8}$'
                    # ),
                ]
            )
        )
    )
    handler(event, {})
