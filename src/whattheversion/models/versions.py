from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime, timezone
import re
from ..utils import ApiError


class Version(BaseModel):
    version: str
    timestamp: datetime
    digest: Optional[str]
    appVersion: Optional[str]

    @validator('timestamp')
    def convert_timestamp_to_utc(cls, v):
        return v.astimezone(timezone.utc)

class Versions(BaseModel):
    versions: List[Version]


    def get_versions_sorted_by_timestamp(self) -> List[Version]:
        """
        returns the versions sorted by timestamp

        :return:
        """

        return sorted(self.versions, key=lambda v: v.timestamp, reverse=True)


    def get_latest_version(self, regexp: Optional[str] = None) -> Version:
        """
        sorts the given versions by timestamp, if a regexp is given filters
        the versions and returns the latest entry
        :param regexp:
        :return:
        """

        sorted_versions = sorted(self.versions, key=lambda v: v.timestamp, reverse=True)

        if regexp:
            p = re.compile(regexp)
            sorted_versions = [ v for v in sorted_versions if p.match(v.version) ]

        if len(sorted_versions) == 0:
            raise ApiError(
                error_message=f'No version found.',
                http_status=404,
            )

        return sorted_versions[0]
