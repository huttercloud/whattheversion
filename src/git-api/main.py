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

def handler(event, context):

    try:
        git_event = parse_git_event(event)
        git_repository = GitRepository(origin=git_event.repository, regexp=git_event.regexp)

        return respond(body=git_repository.quick_debug_function())
    except ApiError as ae:
        return respond(
            body=ae.return_error_response(request_id=context.aws_request_id),
            status_code=ae.httpStatus
        )


if __name__ == '__main__':
    import json
    event = dict(
        body=json.dumps(dict(
            repository='https://github.com/clinton-hall/nzbToMedia'
        ))
    )
    print(handler(event, {}))
