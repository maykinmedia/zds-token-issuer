from typing import Tuple

from django import forms
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from zgw_consumers.constants import APITypes

from .constants import VertrouwelijkheidsAanduiding
from .service import (
    get_besluittypes,
    get_informatieobjecttypes,
    get_scopes,
    get_zaaktypes,
)
from .utils import _get_choices

SCOPE_PREFIXES = {
    APITypes.zrc: "zaken.",
    APITypes.drc: "documenten.",
    APITypes.brc: "besluiten.",
    APITypes.kc: "klanten.",
    APITypes.cmc: "contactmomenten.",
    APITypes.vrc: "verzoeken.",
}


class CreateCredentialsForm(forms.Form):
    label = forms.CharField(
        label=_("Client label"), help_text=_("Human-readable label"),
    )
    prefix = forms.CharField(
        label=_("Prefix"),
        help_text=_(
            "Makes your client ID easier recognizable! "
            "A random string will be appended."
        ),
    )
    superuser = forms.BooleanField(
        label=_("Assign superuser permissions?"),
        required=False,
        help_text=_(
            "Useful for prototyping and getting started quickly, but we "
            "advise against this for serious use cases."
        ),
    )

    def save(self, *args, **kwargs) -> Tuple[str, str]:
        prefix = self.cleaned_data["prefix"]
        random_client_id = get_random_string(length=12)
        client_id = f"{prefix}-{random_client_id}"
        secret = get_random_string(length=32)
        return client_id, secret


class ClientIDForm(forms.Form):
    client_id = forms.CharField(label=_("Client ID"))


class RegisterAuthorizationsForm(ClientIDForm):
    """
    A form to register the authorizations in the AC.
    """

    component = forms.ChoiceField(
        label=_("Component"),
        choices=APITypes.choices,
        help_text=_(
            "The type of component to apply permissions for. "
            "A selection here shows the relevant possible scopes."
        ),
    )
    scopes = forms.MultipleChoiceField(
        label=_("Scopes"),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        help_text=_("Check the scopes that the consumer needs."),
    )

    # optional type limitations
    zaaktype = forms.ChoiceField(
        label=_("Zaaktype"),
        required=False,
        help_text=_("Enkel deze zaaktypen worden ontsloten"),
    )
    informatieobjecttype = forms.ChoiceField(
        label=_("Informatieobjecttype"),
        required=False,
        help_text=_("Enkel deze informatieobjecttypen worden ontsloten."),
    )
    besluittype = forms.ChoiceField(
        label=_("Besluittype"),
        required=False,
        help_text=_("Enkel deze besluittypen worden ontsloten."),
    )
    max_vertrouwelijkheidaanduiding = forms.ChoiceField(
        label=_("Maximale vertrouwelijkheidaanduiding"),
        choices=(("", "-------"),) + VertrouwelijkheidsAanduiding.choices,
        required=False,
        help_text=_(
            "Objecten tot en met deze vertrouwelijkheidaanduiding worden ontsloten"
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["client_id"].help_text = _(
            "A 'Client ID' of the application you wish to configure"
        )

        # fetch and present the available scopes
        scopes = get_scopes()
        self.fields["scopes"].choices = [(scope, scope) for scope in sorted(scopes)]

        # fetch the available zaaktypes
        zaaktypes = get_zaaktypes()
        self.fields["zaaktype"].choices = _get_choices(
            zaaktypes,
            key="zaaktypes",
            transform=lambda x: f"{x['omschrijving']} ({x['identificatie']})",
        )

        informatieobjecttypes = get_informatieobjecttypes()
        self.fields["informatieobjecttype"].choices = _get_choices(
            informatieobjecttypes, key="informatieobjecttypes"
        )

        besluittypes = get_besluittypes()
        self.fields["besluittype"].choices = _get_choices(
            besluittypes, key="besluittypes"
        )

    def clean(self):
        component = self.cleaned_data.get("component")
        scopes = self.cleaned_data.get("scopes")
        max_vertrouwelijkheidaanduiding = self.cleaned_data.get(
            "max_vertrouwelijkheidaanduiding"
        )

        if not component:
            return

        if not scopes:
            return

        scope_prefix = SCOPE_PREFIXES.get(component)
        component_specific_scope_used = scope_prefix is not None and any(
            scope.startswith(scope_prefix) for scope in scopes
        )

        if (
            component in [APITypes.zrc, APITypes.drc]
            and component_specific_scope_used
            and not max_vertrouwelijkheidaanduiding
        ):
            self.add_error(
                "max_vertrouwelijkheidaanduiding",
                forms.ValidationError(
                    _(
                        "You must specify a max_vertrouwelijkheidaanduiding for this component."
                    ),
                    code="required",
                ),
            )

        for _component, field in (
            (APITypes.zrc, "zaaktype"),
            (APITypes.drc, "informatieobjecttype"),
            (APITypes.brc, "besluittype"),
        ):

            if (
                component == _component
                and component_specific_scope_used
                and not self.cleaned_data.get(field)
            ):
                self.add_error(
                    field,
                    forms.ValidationError(
                        _("You must specify the {field} for this component.").format(
                            field=field
                        ),
                        code="required",
                    ),
                )
