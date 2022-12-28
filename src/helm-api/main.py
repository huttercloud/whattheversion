#!/usr/bin/env python3

"""
    lambda function handler for helm-api requests
"""


from whattheversion.utils import ApiError, respond, parse_helm_api_event, setup_logging
from whattheversion.models import HelmResponse
from whattheversion.dynamodb import DynamoDbClient
from whattheversion.eventbus import EventBusClient


def handler(event, context):

    try:
        setup_logging()
        eventbus = EventBusClient()
        db = DynamoDbClient()
        helm_event = parse_helm_api_event(event)

        dynamodb_entry = db.get_helm_entry(registry=helm_event.registry, chart_name=helm_event.chart)
        if not dynamodb_entry or not  dynamodb_entry.versions.versions:
            eventbus.put_helm_event(registry=helm_event.registry, chart=helm_event.chart)
            raise ApiError(
                http_status=404,
                error_message=f'No versions found for helm registry "{helm_event.registry}" and chart "{helm_event.chart}". Sent event to collect '
                              f'version info! Please try again in a minute or two.'
            )

        latest_version = dynamodb_entry.versions.get_latest_version(regexp=helm_event.regexp)
        response = HelmResponse(
            registry=helm_event.registry,
            chart=helm_event.chart,
            version=latest_version.version,
            timestamp=latest_version.timestamp,
            appVersion=latest_version.appVersion,
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
            registry='https://charts.external-secrets.io',
            chart='external-secrets',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
        ))
    )
    print(handler(event, FakeAwsContext()))
