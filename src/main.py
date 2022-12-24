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


import pydantic
from whattheversion.hallo import return_hallo

#from utils.versions import VersionsRequest


def handler(event, context):
    """
        lambda handler
    """

    return return_hallo(event)


    try:
        request = VersionsRequest(**json.loads(event['body']))

        for g in request.git:
            print(f'{g.repository}: {g.get_latest_tag()}')

        for d in request.docker:
            print(f'{d.repository}: {d.get_latest_tag()}')

        for h in request.helm:
            print(f'{h.repository}: {h.get_latest_tag()}')

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
                    dict(
                        repository='k8s.gcr.io/external-dns/external-dns',
                        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/pihole/pihole',
                        regexp='^[0-9]{4}\.[0-9]{1,2}\.[0-9]{1,2}$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/linuxserver/wireguard',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/linuxserver/unifi-controller',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/linuxserver/bazarr',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/linuxserver/nzbhydra2',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/linuxserver/radarr',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/linuxserver/sabnzbd',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/linuxserver/sonarr',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='quay.io/oauth2-proxy/oauth2-proxy',
                        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='registry.hub.docker.com/filebrowser/filebrowser',
                        regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                ],
                helm=[
                    dict(
                        repository='charts.external-secrets.io',
                        chart='external-secrets',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                    dict(
                        repository='argoproj.github.io/argo-helm',
                        chart='argo-cd',
                        regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
                    ),
                ]

            )
        )
    )
    handler(event, {})
