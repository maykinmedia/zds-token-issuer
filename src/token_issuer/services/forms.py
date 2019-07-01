from typing import Tuple

from django import forms
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from zgw_consumers.constants import APITypes

from .constants import VertrouwelijkheidsAanduiding
from .service import (
    get_besluittypes, get_informatieobjecttypes, get_scopes, get_zaaktypes
)
from .utils import _get_choices


class CreateCredentialsForm(forms.Form):
    client_label = forms.CharField(label=_("Client label"), help_text="Human-readable label")

    def save(self, *args, **kwargs) -> Tuple[str, str]:
        label = self.cleaned_data['client_label']
        random_client_id = get_random_string(length=12)
        client_id = f"{label}-{random_client_id}"
        secret = get_random_string(length=32)
        return client_id, secret


class ClientIDForm(forms.Form):
    client_id = forms.CharField(label=_("Client ID"))


class GenerateJWTForm(ClientIDForm):
    secret = forms.CharField(label=_("Secret"))


class RegisterAuthorizationsForm(ClientIDForm):
    """
    A form to register the authorizations in the AC.
    """
    component = forms.ChoiceField(
        label=_("Component"),
        choices=APITypes.choices,
        help_text=_("The type of component to apply permissions for. "
                    "A selection here shows the relevant possible scopes.")
    )
    scopes = forms.MultipleChoiceField(
        label=_("Scopes"),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Check the scopes that the consumer needs.")
    )

    # optional type limitations
    zaaktype = forms.ChoiceField(
        label=_("Zaaktype"), required=False,
        help_text=_("Enkel deze zaaktypen worden ontsloten")
    )
    informatieobjecttype = forms.ChoiceField(
        label=_("Informatieobjecttype"), required=False,
        help_text=_("Enkel deze informatieobjecttypen worden ontsloten.")
    )
    besluittype = forms.ChoiceField(
        label=_("Besluittype"), required=False,
        help_text=_("Enkel deze besluittypen worden ontsloten.")
    )
    max_vertrouwelijkheidaanduiding = forms.ChoiceField(
        label=_("Maximale vertrouwelijkheidaanduiding"),
        choices=(('', '-------'),) + VertrouwelijkheidsAanduiding.choices, required=False,
        help_text=_("Objecten tot en met deze vertrouwelijkheidaanduiding worden ontsloten")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["client_id"].help_text = _("A 'Client ID' of the application you wish to configure")

        # fetch and present the available scopes
        scopes = get_scopes()
        self.fields['scopes'].choices = [(scope, scope) for scope in sorted(scopes)]

        # fetch the available zaaktypes
        zaaktypes = get_zaaktypes()
        self.fields['zaaktype'].choices = _get_choices(
            zaaktypes, key='zaaktypes',
            transform=lambda x: f"{x['omschrijving']} ({x['identificatie']})"
        )

        informatieobjecttypes = get_informatieobjecttypes()
        self.fields['informatieobjecttype'].choices = _get_choices(informatieobjecttypes, key='informatieobjecttypes')

        besluittypes = get_besluittypes()
        self.fields['besluittype'].choices = _get_choices(besluittypes, key='besluittypes')
