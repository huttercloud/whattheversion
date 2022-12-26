#!/usr/bin/env python3

"""
    lambda function handler for git-api requests
"""

# if the lambda function is executed with sam locally the 
# git layer paths need to be setup manually!
import os
if os.getenv('AWS_SAM_LOCAL') == 'true':
    os.environ['PATH'] = ':'.join(['/opt/git/bin', os.environ.get('PATH')])
    os.environ['LD_LIBRARY_PATH'] = ':'.join(['/opt/git/lib', os.environ.get('LD_LIBRARY_PATH')])


from whattheversion.utils import ApiError, respond, parse_git_event
from whattheversion.git import GitRepository
from whattheversion.models import GitResponse
def handler(event, context):

    try:
        git_event = parse_git_event(event)
        git_repository = GitRepository(origin=git_event.repository)

        git_tags = git_repository.get_all_tags()

        tags_to_versions = git_tags.convert_to_versions()
        latest_version = tags_to_versions.get_latest_version(regexp=git_event.regexp)

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
            repository='https://github.com/huttercloud/whattheversion',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
        ))
    )
    print(handler(event, FakeAwsContext()))
