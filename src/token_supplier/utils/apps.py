from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'token_supplier.utils'

    def ready(self):
        from . import checks  # noqa
