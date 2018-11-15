from typing import Tuple

from django import forms
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _


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

    zaaktypes = forms.MultipleChoiceField(
        label=_("Zaaktypes"), required=False,
        widget=forms.CheckboxSelectMultiple
    )
