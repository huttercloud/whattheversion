from ..models import GitRequest
from ..utils import ApiError
from pydantic import ValidationError
import json


def parse_event_body(event: dict) -> dict:
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

def parse_git_event(event: dict) -> GitRequest:
    """
    parse the given event and return a git request
    :param event:
    :return:
    """

    body = parse_event_body(event)

    try:
        return GitRequest(**body)
    except ValidationError as ve:
        raise ApiError(
            http_status=400,
            error_message=ve.json()
        )

