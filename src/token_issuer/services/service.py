from typing import List, Dict, Any
from urllib.parse import urlparse

from django.conf import settings

from zds_client import Client, ClientAuth

from .models import Configuration


def get_zaaktypes() -> List[Dict[str, Any]]:
    config = Configuration.get_solo()

    results = []

    for ztc in config.ztcs.all():
        parsed_url = urlparse(ztc.api_root)

        client = Client('ztc', parsed_url.path)
        client.base_url = ztc._get_api_root()
        client.base_dir = settings.BASE_DIR
        client.auth = ClientAuth(
            client_id=ztc.own_client_id,
            secret=ztc.own_secret,
            scopes=['zds.scopes.zaaktypes.lezen']
        )

        result = {
            'service': ztc,
            'zaaktypes': [],
        }

        catalogi = client.list('catalogus')
        for catalogus in catalogi:
            for url in catalogus['zaaktypen']:
                zaaktype = client.request(url, 'zaaktype_read')
                result['zaaktypes'].append(zaaktype)

        results.append(result)

    return results
