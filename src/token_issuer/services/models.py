from django.db import models
from django.utils.translation import ugettext_lazy as _

import requests


class Service(models.Model):
    label = models.CharField(_("label"), max_length=100)
    api_root = models.CharField(_("api root url"), max_length=255)

    def __str__(self):
        return self.label

    def _get_api_root(self) -> str:
        """
        Return the API root with guaranteed trailing slash
        """
        slash = "/" if not self.api_root.endswith('/') else ""
        return f"{self.api_root}{slash}"

    @property
    def oas_url(self) -> str:
        root = self._get_api_root()
        return f"{root}schema/openapi.yaml"

    def register_client(self, client_id: str, secret: str) -> None:
        root = self._get_api_root()
        endpoint = f"{root}jwtsecret/"

        response = requests.post(endpoint, json={
            'identifier': client_id,
            'secret': secret
        })
        assert response.status_code == 201, "Create went wrong"