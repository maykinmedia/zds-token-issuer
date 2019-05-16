import concurrent.futures
import logging
from typing import Any, Dict, List, Optional

import requests
from zds_client import Client
from zgw_consumers.constants import APITypes

from .models import ServiceProxy as Service
from .utils import cache

logger = logging.getLogger(__name__)

NUM_THREADS = 10


def _get_from_catalogus(client: Client, catalogus: dict, resource: str) -> list:
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as pool:
        futures = [
            pool.submit(client.retrieve, resource, url=url)
            for url in catalogus[f'{resource}n']
        ]
        return [future.result() for future in concurrent.futures.as_completed(futures)]


def _get_from_ztc_catalogi(service: Service, resource: str) -> Dict:
    client = service.build_client()

    result = {
        'service': service,
        f'{resource}s': [],
    }

    try:
        catalogi = client.list('catalogus')
    except (requests.ConnectionError, requests.HTTPError) as e:
        logger.warning("ZTC %r appears to be down, skipping...", service, exc_info=1)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as pool:
        futures = [pool.submit(_get_from_catalogus, client, catalogus, resource) for catalogus in catalogi]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    result[f'{resource}s'] = sum(results, [])

    return result


@cache('ztc:catalogi', duration=60 * 10)
def get_all_from_ztcs(resource: str) -> List[Dict[str, Any]]:
    ztcs = Service.objects.filter(api_type=APITypes.ztc).iterator()

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as pool:
        futures = [pool.submit(_get_from_ztc_catalogi, service, resource) for service in ztcs]
        return [future.result() for future in concurrent.futures.as_completed(futures)]


def get_zaaktypes():
    return get_all_from_ztcs('zaaktype')


def get_informatieobjecttypes():
    return get_all_from_ztcs('informatieobjecttype')


def get_besluittypes():
    return get_all_from_ztcs('besluittype')


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


def _fetch_scopes(service: Service) -> Optional[set]:
    scopes = set()
    client = service.build_client()
    try:
        schema = client.schema
    except requests.ConnectionError:
        logger.warning("Service %r appears to be down, skipping...", service, exc_info=1)
        return
    except requests.HTTPError:
        logger.exception("Could not retrieve schema for service %s", service)
        return

    security_name = _get_security_name(schema)
    if security_name is None:
        return

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


@cache('scopes', duration=60 * 60)
def get_scopes() -> List[str]:
    """
    Check the API schemas of all services and compile a list of all the scopes.
    """
    scopes = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as pool:
        futures = []
        for service in Service.objects.iterator():
            future = pool.submit(_fetch_scopes, service)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            _scopes = future.result()
            if _scopes is None:
                continue
            scopes.update(_scopes)

    return scopes
