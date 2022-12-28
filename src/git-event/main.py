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
    git_remote_tags = git_repository.get_remote_tags()
    dynamodb_entry = db.get_git_entry(origin=git_repository.origin)

    # the dynamodb list is limited to max 500 entries
    # (a dynamidb list can be max 4kb in size, this can easily be reached with
    # bigger helm and docker repos. to ensure the dynamodb is still feed
    # with newer tags the compare_versions function is used in helm and docker
    # this is not possible for git at this stage in the process as git ls remote
    # doesnt return a timestamp.
    # instead lets compare the returned git tags from dynamodb with all tags returned
    # by git ls-remote. this should do the trick for smaller git repos
    # but will always execute the whole git clone/update dynamodb for git repos with more then 500 tags!
    dynamodb_tags = []
    if dynamodb_entry:
        dynamodb_tags = [t.version for t in dynamodb_entry.versions.versions]

    if sorted(dynamodb_tags) != sorted(git_remote_tags):
        git_repository.git_clone()
        git_local_tags = git_repository.get_all_tags()
        db.upsert_git_entry(origin=git_repository.origin, tags=git_local_tags)

if __name__ == '__main__':
    import json

    event = dict(
        detail=dict(
            repository='https://github.com/clinton-hall/nzbToMedia',
        )
    )
    print(handler(event, {}))
