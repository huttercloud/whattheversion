#!/usr/bin/env python3

"""
    lambda function triggered by cron
    parses all given PSKs and sends events to execute updates for
    all entries
"""


import logging
from whattheversion.utils import setup_logging
from whattheversion.eventbus import EventBusClient
from whattheversion.dynamodb import DynamoDbClient
from whattheversion.models import GitRequest, HelmRequest, DockerRequest


setup_logging()
def handler(event, context):
    setup_logging()
    db = DynamoDbClient()
    eventbus = EventBusClient()

    pks = db.get_all_primary_sort_keys()
    for pk in pks:
        p = pk.split('#')
        if p[0] == 'GIT':
            request = GitRequest(repository=f'https://{p[1]}/{p[2]}')
            eventbus.put_git_event(repository=request.repository)
        elif p[0] == 'DOCKER':
            request = DockerRequest(registry=p[1], repository=p[2])
            eventbus.put_docker_event(registry=request.registry, repository=request.repository)
        elif p[0] == 'HELM':
            request = HelmRequest(registry=f'https://{p[1]}', chart=p[2])
            eventbus.put_helm_event(registry=request.registry, chart=request.chart)
        else:
            logging.warning(f'Unknown dynamodb entry: {p}')


if __name__ == '__main__':
    handler({}, {})
