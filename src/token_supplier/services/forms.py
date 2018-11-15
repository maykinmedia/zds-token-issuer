from typing import Tuple

from django import forms
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _


class CreateCredentialsForm(forms.Form):
    label = forms.CharField(label=_("label"), help_text="Human-readable label")

    def save(self, *args, **kwargs) -> Tuple[str, str]:
        label = self.cleaned_data['label']
        random_client_id = get_random_string(length=12)
        client_id = f"{label}-{random_client_id}"
        secret = get_random_string(length=32)
        return client_id, secret
