from pydantic.dataclasses import dataclass
from dataclasses import field
from typing import List, Optional

from ..git.Git import GitRepository
from ..docker import DockerRepository
from ..helm import HelmRepository

@dataclass
class VersionsRequest(object):
    git: Optional[List[GitRepository]] = field(default_factory=list)
    docker: Optional[List[DockerRepository]] = field(default_factory=list)
    helm: Optional[List[HelmRepository]] = field(default_factory=list)

