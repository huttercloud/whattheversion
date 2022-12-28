import requests
from .repository import DockerRepositoryV2, DockerRepositoryQuay


class DockerRegistryV2(object):
    registry: str
    api_base: str

    def __init__(self, registry: str):
        self.registry = registry

        self.api_base = f'https://{self.registry}/v2'

    def get_repository(self, image, **kwargs) -> DockerRepositoryV2:
        return DockerRepositoryV2(repository=image, registry_base_url=self.api_base)


class DockerRegistryDockerHub(DockerRegistryV2):

    def __init__(self, registry: str):
        super().__init__(registry)

    def get_token(self, image: str):
        r = requests.get(
            url=f'https://auth.docker.io/token?service=registry.docker.io&scope=repository:{image}:pull'
        )
        r.raise_for_status()
        return r.json()["token"]

    def get_repository(self, image, **kwargs) -> DockerRepositoryV2:
        headers = {
            'Authorization': f'Bearer {self.get_token(image=image)}',
            'Content-Type': 'application/json',
        }

        return DockerRepositoryV2(repository=image, registry_base_url=self.api_base, http_headers=headers)

class DockerRegistryQuayIo(DockerRegistryV2):

    def __init__(self, registry: str):
        super().__init__(registry)


    def get_repository(self, image, **kwargs) -> DockerRepositoryV2:
        headers = {
            'Content-Type': 'application/json',
        }

        return DockerRepositoryQuay(repository=image, registry_base_url=self.api_base, http_headers=headers)


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
    else:
        return DockerRegistryV2(registry=registry)

    pass
