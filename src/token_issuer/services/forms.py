from typing import Tuple

from django import forms
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from .service import get_zaaktypen


class CreateCredentialsForm(forms.Form):
    client_label = forms.CharField(label=_("Client label"), help_text="Human-readable label")

    def save(self, *args, **kwargs) -> Tuple[str, str]:
        label = self.cleaned_data['client_label']
        random_client_id = get_random_string(length=12)
        client_id = f"{label}-{random_client_id}"
        secret = get_random_string(length=32)
        return client_id, secret


class GenerateJWTForm(forms.Form):
    client_id = forms.CharField(label=_("Client ID"))
    secret = forms.CharField(label=_("Secret"))

    # TODO: add list of scopes from APIs

    zaaktypes = forms.MultipleChoiceField(
        label=_("Zaaktypes"), required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.zaaktypen = get_zaaktypen()

        choices = []
        for item in self.zaaktypen:
            service_label = item['service'].label
            service_address = item['service'].api_root
            optgroup = f"{service_label} ({service_address})"

            values = [
                (zt['url'], f"{zt['omschrijving']}({zt['identificatie']})")
                for zt in item['zaaktypes']
            ]
            choices.append((optgroup, values))

        self.fields['zaaktypes'].choices = choices
