import logging
from typing import Any, Dict, List
from urllib.parse import urlparse

from django.conf import settings

import requests
from zds_client import Client, ClientAuth

from .models import Configuration, Service

logger = logging.getLogger(__name__)


def client_for_service(service: Service, auth=False, scopes: list=None) -> Client:
    parsed_url = urlparse(service.api_root)

    client = Client('service', parsed_url.path)

    client.base_url = service._get_api_root()
    client.base_dir = settings.BASE_DIR

    if auth:
        client.auth = ClientAuth(
            client_id=service.own_client_id,
            secret=service.own_secret,
            scopes=scopes
        )

    return client


def get_zaaktypes() -> List[Dict[str, Any]]:
    config = Configuration.get_solo()

    results = []

    for ztc in config.ztcs.all():
        client = client_for_service(ztc, auth=True, scopes=['zds.scopes.zaaktypes.lezen'])

        result = {
            'service': ztc,
            'zaaktypes': [],
        }

        try:
            catalogi = client.list('catalogus')
        except requests.ConnectionError:
            logger.warning("ZTC %r appears to be down, skipping...", ztc, exc_info=1)
            continue

        for catalogus in catalogi:
            for url in catalogus['zaaktypen']:
                zaaktype = client.request(url, 'zaaktype_read')
                result['zaaktypes'].append(zaaktype)

        results.append(result)

    return results


def _get_security_name(schema):
    security_schemes = schema['components']['securitySchemes']
    for name, scheme in security_schemes.items():
        if scheme.get('bearerFormat') == 'JWT':
            return name

    return None


def clean_scopes(scopes: List[str]) -> List[str]:
    result = []
    for scope in scopes:
        if '|' in scope:
            bits = [bit for bit in scope.strip('(').strip(')').split(' | ')]
            result += clean_scopes(bits)
        else:
            result.append(scope)
    return result


def get_scopes() -> List[str]:
    """
    Check the API schemas of all services and compile a list of all the scopes.
    """
    scopes = set()

    for service in Service.objects.iterator():
        client = client_for_service(service)
        try:
            schema = client.schema
        except requests.ConnectionError:
            logger.warning("Service %r appears to be down, skipping...", service, exc_info=1)
            continue
        except requests.HTTPError:
            logger.exception("Could not retrieve schema for service %s", service)
            continue

        security_name = _get_security_name(schema)
        if security_name is None:
            continue

        for path_options in client.schema['paths'].values():
            for method in path_options.values():
                if not isinstance(method, dict):  # parameters list
                    continue

                if 'security' not in method:
                    continue

                for security in method['security']:
                    _scopes = security.get(security_name)
                    if _scopes is None:
                        continue

                    scopes = scopes.union(clean_scopes(_scopes))

    return scopes
