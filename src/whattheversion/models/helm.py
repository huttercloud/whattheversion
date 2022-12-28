from pydantic import BaseModel, AnyHttpUrl
from typing import Optional, List
from datetime import datetime
from .versions import Versions, Version

class HelmRequest(BaseModel):
    registry: AnyHttpUrl
    chart: str
    regexp: Optional[str]


class HelmResponse(BaseModel):
    registry: AnyHttpUrl
    chart: str
    version: str
    timestamp: datetime
    appVersion: Optional[str]


class HelmChartEntry(BaseModel):
    appVersion: Optional[str]
    version: str
    created: datetime


class HelmChart(BaseModel):
    name: str
    entries: List[HelmChartEntry]


    def convert_to_versions(self) -> Versions:
        v = Versions(versions=[])

        for e in self.entries:
            v.versions.append(Version(version=e.version, timestamp=e.created, appVersion=e.appVersion))

        return v