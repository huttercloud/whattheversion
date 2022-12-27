#!/usr/bin/env python3

"""
    lambda function handler for helm-api requests
"""


from whattheversion.utils import ApiError, respond, parse_helm_event, setup_logging
from whattheversion.helm import HelmRegistry
from whattheversion.models import HelmResponse

setup_logging()
def handler(event, context):

    try:
        helm_event = parse_helm_event(event)
        helm_registry = HelmRegistry(registry=helm_event.registry)
        helm_chart = helm_registry.get_helm_chart(name=helm_event.chart)

        chart_to_versions = helm_chart.convert_to_versions()
        latest_version = chart_to_versions.get_latest_version(regexp=helm_event.regexp)


        response = HelmResponse(
            registry=helm_registry.registry,
            chart=helm_chart.name,
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
            registry='https://charts.external-secrets.io',
            chart='external-secrets',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
        ))
    )
    print(handler(event, FakeAwsContext()))
