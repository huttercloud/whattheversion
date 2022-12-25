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



from git.cmd import Git
from whattheversion.utils import ApiError, respond, parse_git_event

def handler(event, context):

    try:
        git_event = parse_git_event(event)
        print(git_event)
        return respond(body=git_event.json())
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
    handler(event, {})
