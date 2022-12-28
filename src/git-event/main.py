#!/usr/bin/env python3

"""
    lambda function handler for git-event requests

    the git events sent by event bridge instruct the lambda to parse the given git repository and
    populate the dynamodb table
"""


import os
os.environ['PATH'] = ':'.join(['/opt/git/bin', os.environ.get('PATH')])
os.environ['LD_LIBRARY_PATH'] = ':'.join(['/opt/git/lib', os.environ.get('LD_LIBRARY_PATH', '')])

import logging
from whattheversion.utils import setup_logging
from whattheversion.utils import parse_git_eventbridge_event
from whattheversion.git import GitRepository
from whattheversion.dynamodb import DynamoDbClient

def handler(event, context):

    setup_logging()
    db = DynamoDbClient()
    git_event = parse_git_eventbridge_event(event)
    git_repository = GitRepository(origin=git_event.repository)

    git_repository.git_clone()
    git_local_tags = git_repository.get_all_tags()
    db.upsert_git_entry(origin=git_repository.origin, tags=git_local_tags)


if __name__ == '__main__':
    event = dict(
        detail=dict(
            repository='https://github.com/clinton-hall/nzbToMedia',
        )
    )
    handler(event, {})