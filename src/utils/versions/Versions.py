from pydantic.dataclasses import dataclass
from typing import List, Optional

from ..git.Git import GitRepository
from ..docker import DockerRepository
from ..helm import HelmRepository

@dataclass
class VersionsRequest(object):
    git: Optional[List[GitRepository]] = list()
    docker: Optional[List[DockerRepository]] = list()
    helm: Optional[List[HelmRepository]] = list()

