import requests
from ..utils import ApiError
from ..models import HelmChart, HelmChartEntry
from typing import Dict
import logging
from yaml import load, Loader, YAMLError

class HelmRegistry(object):
    registry: str
    index: Dict

    def __init__(self, registry: str):
        self.registry = registry
        self._parse_helm_index(index=self._download_helm_index())

    def _download_helm_index(self) -> str:
        """
        download the index.yaml from the registry
        :return:
        """

        try:
            logging.debug(f'Downloading {self.registry}/index.yaml')
            r = requests.get(url=f'{self.registry}/index.yaml', allow_redirects=True)
            r.raise_for_status()
            return r.text
        except requests.exceptions.HTTPError as he:
            logging.error(he.response.reason)
            raise ApiError(
                http_status=he.response.status_code,
                error_message=f'Unable to download helm registry index: {he.response.reason}'
            )
        except requests.exceptions.RequestException as re:
            logging.error(re.response.reason)
            raise ApiError(
                http_status=500,
                error_message=str(re.args[0].reason)
            )


    def _parse_helm_index(self, index: str):
        """
        parse the downlaoded helm index and store it for later use
        :param index:
        :return:
        """

        try:
            self.index = load(index, Loader=Loader)
        except YAMLError as ye:
            logging.error(ye)
            raise ApiError(
                http_status=500,
                error_message=f'Unable to parse helm registry index.yaml'
            )


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