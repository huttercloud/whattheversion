import boto3
from typing import Any

from ..models import UpsertDynamoDBEvent, UpsertGitEventDetail, UpsertDockerEventDetail, UpsertHelmEventDetail

class EventBusClient(object):
    client: Any

    def __init__(self):
        self.client = boto3.client('events')


    def put_git_event(self, repository: str):
        """
        creates a custom git event in eventbridge
        :param repository:
        :return:
        """

        event = UpsertDynamoDBEvent().dict()

        event['Detail'] = UpsertGitEventDetail(
            repository=repository
        ).json()

        self.client.put_events(
            Entries=[
                event
            ]
        )

    def put_helm_event(self, registry: str, chart: str):
        """
        creates a custom helm event in eventbridge
        :param registry:
        :param chart
        :return:
        """

        event = UpsertDynamoDBEvent().dict()

        event['Detail'] = UpsertHelmEventDetail(
            registry=registry,
            chart=chart
        ).json()

        self.client.put_events(
            Entries=[
                event
            ]
        )

    def put_docker_event(self, registry: str, repository: str):
        """
        creates a custom docker event in eventbridge
        :param registry:
        :param repository
        :return:
        """

        event = UpsertDynamoDBEvent().dict()

        event['Detail'] = UpsertDockerEventDetail(
            registry=registry,
            repository=repository
        ).json()

        self.client.put_events(
            Entries=[
                event
            ]
        )
