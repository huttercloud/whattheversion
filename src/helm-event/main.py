#!/usr/bin/env python3

"""
    lambda function handler for helm-api requests
"""




from whattheversion.utils import respond, parse_helm_eventbridge_event, setup_logging
from whattheversion.helm import HelmRegistry
from whattheversion.models import HelmResponse, compare_versions
from whattheversion.dynamodb import DynamoDbClient


def handler(event, context):

    setup_logging()
    db = DynamoDbClient()
    helm_event = parse_helm_eventbridge_event(event)
    helm_registry = HelmRegistry(registry=helm_event.registry)
    helm_chart = helm_registry.get_helm_chart(name=helm_event.chart)
    dynamodb_entry = db.get_helm_entry(registry=helm_registry.registry, chart_name=helm_chart.name)

    are_latest_versions_the_same = False
    if dynamodb_entry:
        are_latest_versions_the_same = compare_versions(
            versions_a=dynamodb_entry.versions.get_versions_sorted_by_timestamp()[0],
            versions_b=helm_chart.convert_to_versions().get_versions_sorted_by_timestamp()[0]
        )

    if not are_latest_versions_the_same:
        db.upsert_helm_entry(registry=helm_registry.registry, chart=helm_chart)


if __name__ == '__main__':
    event = dict(
        detail=dict(
            registry='https://charts.external-secrets.io',
            chart='external-secrets',
        )
    )
    handler(event, {})