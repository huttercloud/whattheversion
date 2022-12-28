import requests
from ..utils import ApiError
from ..models import HelmChart, HelmChartEntry
from typing import Dict
from .helmtojson import download_and_convert_helm_index_to_json

class HelmRegistry(object):
    registry: str
    index: Dict

    def __init__(self, registry: str):
        self.registry = registry
        self.index = download_and_convert_helm_index_to_json(index_url=f'{self.registry}/index.yaml')

    def get_helm_chart(self, name: str) -> HelmChart:
        """
        find the specified chart in the index.yaml and return all its versions etc
        :param chart:
        :return:
        """

        chart = HelmChart(name=name, entries=[])

        for entry in self.index.get('entries', {}).get(name, []):
            chart.entries.append(HelmChartEntry(**entry))

        return chart