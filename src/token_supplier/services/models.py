from django.db import models
from django.utils.translation import ugettext_lazy as _


class Service(models.Model):
    label = models.CharField(_("label"), max_length=100)
    api_root = models.CharField(_("address"), max_length=255)

    def __str__(self):
        return self.label

    @property
    def oas_url(self) -> str:
        slash = "/" if not self.api_root.endswith('/') else ""
        return f"{self.api_root}{slash}schema/openapi.yaml"

    def register_client(self, client_id: str, secret: str) -> None:
        pass
