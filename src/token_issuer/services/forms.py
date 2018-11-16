from typing import Tuple

from django import forms
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from .service import get_scopes, get_zaaktypes


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

    scopes = forms.MultipleChoiceField(
        label=_("Scopes"), required=False,
        widget=forms.CheckboxSelectMultiple
    )

    zaaktypes = forms.MultipleChoiceField(
        label=_("Zaaktypes"), required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # fetch the available zaaktypes
        self.zaaktypes = get_zaaktypes()

        zt_choices = []
        for item in self.zaaktypes:
            service_label = item['service'].label
            service_address = item['service'].api_root
            optgroup = f"{service_label} ({service_address})"

            values = [
                (zt['url'], f"{zt['omschrijving']}({zt['identificatie']})")
                for zt in item['zaaktypes']
            ]
            zt_choices.append((optgroup, values))

        self.fields['zaaktypes'].choices = zt_choices

        # dynamically retrieve the scopes
        self.fields['scopes'].choices = [
            (scope, scope) for scope in sorted(get_scopes())
        ]
