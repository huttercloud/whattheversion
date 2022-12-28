#!/usr/bin/env python3

"""
    lambda function handler for helm-api requests
"""


import logging
from whattheversion.utils import parse_helm_eventbridge_event, setup_logging
from whattheversion.helm import HelmRegistry
from whattheversion.dynamodb import DynamoDbClient


def handler(event, context):

    setup_logging()
    db = DynamoDbClient()
    helm_event = parse_helm_eventbridge_event(event)
    helm_registry = HelmRegistry(registry=helm_event.registry)
    helm_chart = helm_registry.get_helm_chart(name=helm_event.chart)
    db.upsert_helm_entry(registry=helm_registry.registry, chart=helm_chart)


if __name__ == '__main__':
    event = dict(
        detail=dict(
            registry='https://charts.external-secrets.io',
            chart='external-secrets',
        )
    )
    handler(event, {})