#!/usr/bin/env python3

"""
    lambda function handler for git-api requests
"""


import logging
from whattheversion.utils import ApiError, respond, parse_git_api_event, setup_logging
from whattheversion.models import GitResponse
from whattheversion.dynamodb import DynamoDbClient
from whattheversion.eventbus import EventBusClient

def handler(event, context):
    try:
        setup_logging()
        eventbus = EventBusClient()
        db = DynamoDbClient()
        git_event = parse_git_api_event(event)

        dynamodb_entry = db.get_git_entry(origin=git_event.repository)
        if not dynamodb_entry or not  dynamodb_entry.versions.versions:
            eventbus.put_git_event(repository=git_event.repository)
            raise ApiError(
                http_status=404,
                error_message=f'No versions found for git repository "{git_event.repository}". Sent event to collect '
                              f'version info! Please try again in a minute or two.'
            )

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
