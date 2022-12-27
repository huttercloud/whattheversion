#!/usr/bin/env python3

"""
    lambda function handler for docker-api requests
"""


from whattheversion.utils import ApiError, respond, parse_docker_event, setup_logging
from whattheversion.docker import create_docker_registry
from whattheversion.models import DockerResponse

setup_logging()
def handler(event, context):

    try:
        docker_event = parse_docker_event(event)

        docker_registry = create_docker_registry(registry=docker_event.registry)
        docker_repository = docker_registry.get_repository(image=docker_event.image)


        tags_to_versions = docker_repository.convert_to_versions()
        latest_version = tags_to_versions.get_latest_version(regexp=docker_event.regexp)

        response = DockerResponse(
            registry=docker_registry.registry,
            version=latest_version.version,
            timestamp=latest_version.timestamp,
            image=docker_repository.repository
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
            image='linuxserver/sabnzbd',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$'
        ))
    )
    print(handler(event, FakeAwsContext()))
