import requests
from .repository import DockerRepositoryV2, DockerRepositoryQuay, DockerRepositoryDockerHub


class DockerRegistryV2(object):
    registry: str
    api_base: str

    def __init__(self, registry: str):
        self.registry = registry

        self.api_base = f'https://{self.registry}/v2'

    def get_repository(self, repository, **kwargs) -> DockerRepositoryV2:
        return DockerRepositoryV2(repository=repository, registry_base_url=self.api_base)


class DockerRegistryDockerHub(DockerRegistryV2):

    def __init__(self, registry: str):
        super().__init__(registry)

    def get_repository(self, repository, **kwargs) -> DockerRepositoryDockerHub:
        headers = {
            'Content-Type': 'application/json',
        }

        return DockerRepositoryDockerHub(repository=repository, registry_base_url=self.api_base, http_headers=headers)

class DockerRegistryQuayIo(DockerRegistryV2):

    def __init__(self, registry: str):
        super().__init__(registry)


    def get_repository(self, repository, **kwargs) -> DockerRepositoryV2:
        headers = {
            'Content-Type': 'application/json',
        }

        return DockerRepositoryQuay(repository=repository, registry_base_url=self.api_base, http_headers=headers)


class DockerRegistryGithub(DockerRegistryV2):
    def __init__(self, registry: str):
        super().__init__(registry)

    def get_repository(self, repository, **kwargs) -> DockerRepositoryV2:
        headers = {
            'Content-Type': 'application/json',
        }

        token_Params = dict(
            scope=f'repository:{repository}:pull'
        )
        r = requests.get(url=f'https://{self.registry}/token',params=token_Params)
        r.raise_for_status()
        headers['Authorization'] = f'Bearer {r.json()["token"]}'

        return DockerRepositoryV2(repository=repository, registry_base_url=self.api_base, http_headers=headers)

def create_docker_registry(registry: str) -> DockerRegistryV2:
    """
    initialize a docker registry depending on the given registry name
    :param registry:
    :return:
    """

    if registry == 'registry.hub.docker.com':
        return DockerRegistryDockerHub(registry=registry)
    elif registry == 'quay.io':
        return DockerRegistryQuayIo(registry=registry)
    elif registry == 'ghcr.io':
        return DockerRegistryGithub(registry=registry)
    else:
        return DockerRegistryV2(registry=registry)
