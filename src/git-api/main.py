#!/usr/bin/env python3

"""
    lambda function handler for git-api requests
"""

# if the lambda function is executed with sam locally the 
# git layer paths need to be setup manually!
import os
import logging

from whattheversion.utils import is_local_dev, setup_logging
setup_logging()
if is_local_dev():
    os.environ['PATH'] = ':'.join(['/opt/git/bin', os.environ.get('PATH')])
    os.environ['LD_LIBRARY_PATH'] = ':'.join(['/opt/git/lib', os.environ.get('LD_LIBRARY_PATH', '')])

from whattheversion.utils import ApiError, respond, parse_git_event
from whattheversion.git import GitRepository
from whattheversion.models import GitResponse
from whattheversion.dynamodb import DynamoDbClient

def handler(event, context):

    try:
        db = DynamoDbClient()
        git_event = parse_git_event(event)
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

        if dynamodb_tags.sort() != git_remote_tags.sort():
            git_repository.git_clone()
            git_local_tags = git_repository.get_all_tags()
            db.upsert_git_entry(origin=git_repository.origin, tags=git_local_tags)
            dynamodb_entry = db.get_git_entry(origin=git_repository.origin)

        latest_version = dynamodb_entry.versions.get_latest_version(regexp=git_event.regexp)

        response = GitResponse(
            repository=git_event.repository,
            version=latest_version.version,
            timestamp=latest_version.timestamp,
        )

        return respond(body=response.json())
    except ApiError as ae:
        return respond(
            body=ae.return_error_response(request_id=context.aws_request_id),
            status_code=ae.httpStatus
        )


if __name__ == '__main__':
    import json
    from whattheversion.utils import FakeAwsContext
    event = dict(
        body=json.dumps(dict(
            #repository='https://github.com/huttercloud/whattheversion',
            repository='https://github.com/clinton-hall/nzbToMedia',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
        ))
    )
    print(handler(event, FakeAwsContext()))
