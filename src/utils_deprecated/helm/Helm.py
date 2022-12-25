from pydantic.dataclasses import dataclass
from typing import Any, List
import requests
from yaml import load, Loader
import re
from datetime import datetime
@dataclass()
class HelmRepository(object):
    """
    retrieve latest helm tag from helm repository
    """
    repository: str
    chart: str
    regexp: str


    def download_and_parse_index_yaml(self) -> Any:
        """
        downloads the index yaml of the given helm repository
        :return:
        """

        r = requests.get(url=f'https://{self.repository}/index.yaml', allow_redirects=True)
        r.raise_for_status()

        return load(r.text, Loader=Loader)


    def get_all_tags(self) -> List[str]:

        filtered_entries = {}
        reg = re.compile(self.regexp)
        yml = self.download_and_parse_index_yaml()
        for entry in yml['entries'].get(self.chart, []):
            if not reg.match(entry['version']):
                continue

            # only parse day and time information "YYYY-08-07THH:MM:SS" (length: 19)
            ts = entry["created"][0:19]

            filtered_entries[entry['version']] = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S')

        return [a[0] for a in sorted(filtered_entries.items(), key=lambda i: i[1])]


    def get_latest_tag(self) -> str:
        tags = self.get_all_tags()
        return tags[-1]