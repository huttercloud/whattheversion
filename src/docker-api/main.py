
#!/usr/bin/env python3

"""
    lambda function handler for docker-api requests
"""


from whattheversion.utils import ApiError, respond, parse_docker_api_event, setup_logging
from whattheversion.models import DockerResponse
from whattheversion.dynamodb import DynamoDbClient
from whattheversion.eventbus import EventBusClient


setup_logging()
def handler(event, context):

    try:
        setup_logging()
        eventbus = EventBusClient()
        db = DynamoDbClient()
        docker_event = parse_docker_api_event(event)

        dynamodb_entry = db.get_docker_entry(registry=docker_event.registry,
                                             repository=docker_event.repository)
        if not dynamodb_entry or not  dynamodb_entry.versions.versions:
            eventbus.put_docker_event(registry=docker_event.registry, repository=docker_event.repository)
            raise ApiError(
                http_status=404,
                error_message=f'No versions found for docker registry "{docker_event.registry}" and repository "{docker_event.repository}". Sent event to collect '
                              f'version info! Please try again in a minute or two.'
            )

        latest_version = dynamodb_entry.versions.get_latest_version(regexp=docker_event.regexp)

        response = DockerResponse(
            registry=docker_event.registry,
            version=latest_version.version,
            timestamp=latest_version.timestamp,
            repository=docker_event.repository,
            digest=latest_version.digest,
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
            # # dockerhub examples
            # repository='linuxserver/sabnzbd',
            # regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
            repository='filebrowser/filebrowser',
            regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',

            # k8s.gcr.io example
            # registry='k8s.gcr.io',
            # repository='external-dns/external-dns',
            # regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$'
            #
            # # quay.io example
            # registry='quay.io',
            # repository='oauth2-proxy/oauth2-proxy',
            # regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$'
        ))
    )
    print(handler(event, FakeAwsContext()))



