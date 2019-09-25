import json
import os
import sys
import uuid

from django.contrib.auth.management.commands.createsuperuser import (
    NotRunningInTTYException,
)
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Generate the fixtures in JSON format for all type of services"

    def add_arguments(self, parser):
        parser.add_argument("--client-id", "-c")
        parser.add_argument("--secret", "-s")
        parser.add_argument("--output-dir", default="/tmp/fixtures")

    def handle(self, **options):
        self.stdin = options.get("stdin", sys.stdin)

        output_dir = options["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        client_id = options["client_id"]
        secret = options["secret"]

        if not client_id or not secret:
            if hasattr(self.stdin, 'isatty') and not self.stdin.isatty():
                raise NotRunningInTTYException("Not running in a TTY")

            if not client_id:
                client_id = self.get_input_data("Client ID: ")

            if not secret:
                secret = self.get_input_data("Secret: ")

        ac_data = [{
            "model": "authorizations.applicatie",
            "pk": 999,
            "fields": {
                "uuid": str(uuid.uuid4()),
                "client_ids": [client_id],
                "label": "My superuser client",
                "heeft_alle_autorisaties": True
            }
        }]

        with open(os.path.join(output_dir, "ac.json"), "w") as outfile:
            json.dump(ac_data, outfile, indent=4)

        api_credential = {
            "model": "vng_api_common.jwtsecret",
            "pk": 999,
            "fields": {
                "identifier": client_id,
                "secret": secret,
            }
        }

        ports = [8000, 8001, 8002, 8003, 8004, 8005]
        component_data = [api_credential] + [
            {
                "model": "vng_api_common.apicredential",
                "pk": 999 + i,
                "fields": {
                    "api_root": f"http://localhost:{port}/api/v1/",
                    "label": f"Service at localhost:{port}",
                    "client_id": client_id,
                    "secret": secret,
                    "user_id": "system",
                    "user_representation": "System",
                }
            }
            for i, port in enumerate(ports)
        ]

        with open(os.path.join(output_dir, "auth.json"), "w") as outfile:
            json.dump(component_data, outfile, indent=4)

    def get_input_data(self, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if default and raw_value == '':
            raw_value = default
        return raw_value
