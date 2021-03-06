import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, View

from zds_client import ClientAuth

from .forms import ClientIDForm, CreateCredentialsForm, RegisterAuthorizationsForm
from .models import RegistrationError, ServiceProxy as Service
from .service import (
    add_authorization,
    create_superuser_client,
    get_authorizations,
    make_superuser,
)

logger = logging.getLogger(__name__)

NUM_THREADS = 10


def _register_client(
    service: Service, client_id: str, secret: str, request: HttpRequest
):
    logger.debug("Registering credentials to %s", service)
    try:
        service.register_client(client_id, secret)
        logger.info("Registered %s with %s", client_id, service)
    except RegistrationError:
        logger.error("Could not register with service %s", service, exc_info=1)
        messages.warning(request, f"Could not register with service '{service}'")


class ResetView(View):
    def post(self, request, *args, **kwargs):
        next_page = request.META.get("HTTP_REFERER", reverse("index"))
        if not is_safe_url(next_page, settings.ALLOWED_HOSTS):
            logger.warning("Found unsafe next_page: %s", next_page)
            next_page = reverse("index")

        for key in ["client_id", "secret", "superuser", "credentials"]:
            if key in request.session:
                del request.session[key]

        return redirect(next_page)


class CreateCredentialsView(SuccessMessageMixin, FormView):
    template_name = "services/client.html"
    form_class = CreateCredentialsForm
    success_message = _("Your credentials have been registered with the services")
    success_url = reverse_lazy("index")

    def get_services(self):
        return Service.objects.iterator()

    def form_valid(self, form):
        client_id, secret = form.save()
        superuser = form.cleaned_data["superuser"]

        self.request.session["superuser"] = superuser
        self.request.session["client_id"] = client_id
        self.request.session["secret"] = secret

        # register with services
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as pool:
            for service in self.get_services():
                pool.submit(_register_client, service, client_id, secret, self.request)
            messages.success(self.request, _("Client ID registered with services."))

        # register the application
        if superuser:
            create_superuser_client(client_id, form.cleaned_data["label"])
            messages.success(
                self.request, _("Application registered with superuser permissions.")
            )

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["services"] = self.get_services()

        # put a JWT in the session if it's not there yet
        can_generate_creds = (
            "client_id" in self.request.session and "secret" in self.request.session
        )
        if can_generate_creds and "credentials" not in self.request.session:
            auth = ClientAuth(
                client_id=self.request.session["client_id"],
                secret=self.request.session["secret"],
            )
            self.request.session["credentials"] = auth.credentials()

        return context


class SetClientIDMixin:
    def _set_client_id(self, form) -> str:
        client_id = form.cleaned_data["client_id"]
        if (
            "client_id" not in self.request.session
            or self.request.session["client_id"] != client_id
        ):
            self.request.session["client_id"] = client_id
        return client_id

    def _get_client_id(self) -> Optional[str]:
        return self.request.session.get("client_id")

    def get_initial(self):
        initial = super().get_initial()
        initial.update(client_id=self._get_client_id() or "",)
        return initial


class ViewAuthView(SetClientIDMixin, FormView):
    form_class = ClientIDForm
    template_name = "services/view_auth.html"
    success_url = reverse_lazy("view-auth")

    def form_valid(self, form):
        self._set_client_id(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self._get_client_id()
        context["application"] = get_authorizations(client_id)
        return context


class SetAuthorizationsView(SuccessMessageMixin, SetClientIDMixin, FormView):
    form_class = RegisterAuthorizationsForm
    template_name = "services/set_auth.html"
    success_url = reverse_lazy("set-auth")
    success_message = _("The authorization has been added")

    def get_form_class(self):
        if "superuser" in self.request.POST:
            return ClientIDForm
        return super().get_form_class()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self._get_client_id()
        context["authorizations"] = get_authorizations(client_id)["autorisaties"]
        return context

    def form_valid(self, form):
        client_id = self._set_client_id(form)
        if "superuser" in self.request.POST:
            make_superuser(client_id)
        else:
            add_authorization(client_id, form.cleaned_data)
        return super().form_valid(form)
