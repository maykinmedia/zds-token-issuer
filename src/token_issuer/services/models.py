from urllib.parse import urljoin

from django.db import models
from django.utils.translation import ugettext_lazy as _

import requests
from solo.models import SingletonModel
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service as _Service


class RegistrationError(Exception):
    pass


class Service(models.Model):
    label = models.CharField(_("label"), max_length=100)
    api_root = models.CharField(_("api root url"), max_length=255)

    own_client_id = models.CharField(max_length=255, blank=True)
    own_secret = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.api_root.endswith('/'):
            self.api_root = f"{self.api_root}/"
        super().save(*args, **kwargs)

    @property
    def oas_url(self) -> str:
        return urljoin(self.api_root, 'schema/openapi.yaml')

    def register_client(self, client_id: str, secret: str) -> None:
        endpoint = urljoin(self.api_root, 'jwtsecret/')
        try:
            response = requests.post(endpoint, json={
                'identifier': client_id,
                'secret': secret
            })
        except requests.ConnectionError as exc:
            raise RegistrationError() from exc
        assert response.status_code == 201, "Create went wrong"


class ServiceProxy(_Service):
    class Meta:
        proxy = True

    @property
    def oas_url(self) -> str:
        return urljoin(self.api_root, 'schema/openapi.yaml')

    def register_client(self, client_id: str, secret: str) -> None:
        endpoint = urljoin(self.api_root, 'jwtsecret/')
        try:
            response = requests.post(endpoint, json={
                'identifier': client_id,
                'secret': secret
            })
        except requests.ConnectionError as exc:
            raise RegistrationError() from exc
        assert response.status_code == 201, "Create went wrong"


class Configuration(SingletonModel):
    primary_ac = models.ForeignKey(
        "zgw_consumers.Service", on_delete=models.SET_NULL,
        null=True,
        related_name="+",
        limit_choices_to={'api_type': APITypes.ac},
        verbose_name=_("Authorization component (AC)"),
    )

    class Meta:
        verbose_name = _("Service configuration")

    def __str__(self):
        return "Service configuration"
