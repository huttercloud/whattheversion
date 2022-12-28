#!/usr/bin/env python3

"""
    query versions used in hutter.cloud/infrastructure and hutter.cloud/applications
"""

import requests
import json
import logging
import click

VERSIONS=dict(
    git=[
        dict(
            repository='https://github.com/clinton-hall/nzbToMedia.git',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        )
    ],
    docker=[
        dict(
            registry='k8s.gcr.io',
            image='external-dns/external-dns',
            regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='pihole/pihole',
            regexp='^[0-9]{4}\.[0-9]{1,2}\.[0-9]{1,2}$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='linuxserver/wireguard',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='linuxserver/unifi-controller',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='linuxserver/bazarr',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='linuxserver/nzbhydra2',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='linuxserver/radarr',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='linuxserver/sabnzbd',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='linuxserver/sonarr',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='quay.io',
            image='oauth2-proxy/oauth2-proxy',
            regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='registry.hub.docker.com',
            image='filebrowser/filebrowser',
            regexp='^v[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
    ],
    helm=[
        dict(
            registry='https://charts.external-secrets.io',
            chart='external-secrets',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
        dict(
            registry='https://argoproj.github.io/argo-helm',
            chart='argo-cd',
            regexp='^[0-9]+\.?[0-9]+\.?[0-9]+$',
        ),
    ]
)


@click.command()
@click.option('--endpoint', default='https://whattheversion.hutter.cloud/api')
def query(endpoint: str):
    results=dict(
        git=[],
        docker=[],
        helm=[],
    )

    # # query git versions
    for git in VERSIONS.get('git', []):
        try:
            r = requests.post(url=f'{endpoint}/git', json=git)
            r.raise_for_status()
            results.get('git').append(r.json())
        except Exception as e:
            logging.warning(f'Error when retrieving versions for git:{git}: {e}')
    # # query helm versions
    for helm in VERSIONS.get('helm', []):
        try:
            r = requests.post(url=f'{endpoint}/helm', json=helm)
            r.raise_for_status()
            results.get('helm').append(r.json())
        except Exception as e:
            logging.warning(f'Error when retrieving versions for helm:{helm}: {e}')
    # query docker versions
    for docker in VERSIONS.get('docker', []):
        try:
            r = requests.post(url=f'{endpoint}/docker', json=docker)
            r.raise_for_status()
            results.get('docker').append(r.json())
        except Exception as e:
            logging.warning(f'Error when retrieving versions for docker:{docker}: {e}')

    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    query()
