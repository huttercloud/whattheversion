from ..models import GitRequest, HelmRequest, DockerRequest
from ..utils import ApiError
from pydantic import ValidationError
import json


def parse_api_event_body(event: dict) -> dict:
    """
    parse the given event body
    :param event:
    :return:
    """

    try:
        return json.loads(event.get('body'))
    except json.JSONDecodeError as je:
        raise ApiError(
            http_status=400,
            error_message=je.msg
        )


def parse_git_api_event(event: dict) -> GitRequest:
    """
    parse the given event and return a git request
    :param event:
    :return:
    """

    body = parse_api_event_body(event)

    try:
        return GitRequest(**body)
    except ValidationError as ve:
        raise ApiError(
            http_status=400,
            error_message=ve.json()
        )

def parse_git_eventbridge_event(event: dict) -> GitRequest:
    """
    parse the given eventbridge git event and give back a git request
    :param event:
    :return:
    """

    return GitRequest(**event.get('detail'))


def parse_helm_api_event(event: dict) -> HelmRequest:
    """
    parse the given event and return a helm request
    :param event:
    :return:
    """

    body = parse_api_event_body(event)

    try:
        return HelmRequest(**body)
    except ValidationError as ve:
        raise ApiError(
            http_status=400,
            error_message=ve.json()
        )

def parse_helm_eventbridge_event(event: dict) -> HelmRequest:
    """
    parse the given eventbridge helm event and give back a helm request
    :param event:
    :return:
    """

    return HelmRequest(**event.get('detail'))

def parse_docker_event(event: dict) -> DockerRequest:
    """
    parse the given event and return a docker request
    :param event:
    :return:
    """

    body = parse_api_event_body(event)

    try:
        return DockerRequest(**body)
    except ValidationError as ve:
        raise ApiError(
            http_status=400,
            error_message=ve.json()
        )