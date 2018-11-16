from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from zds_client import ClientAuth

from .forms import CreateCredentialsForm, GenerateJWTForm
from .models import Service


class CreateCredentialsView(SuccessMessageMixin, FormView):
    template_name = 'services/client.html'
    form_class = CreateCredentialsForm
    success_message = _("Your credentials have been registered with the services")
    success_url = reverse_lazy('index')

    def get_services(self):
        return Service.objects.iterator()

    def form_valid(self, form):
        client_id, secret = form.save()

        self.request.session['client_id'] = client_id
        self.request.session['secret'] = secret

        for service in self.get_services():
            service.register_client(client_id, secret)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = self.get_services()
        return context


class GenerateJWTView(FormView):
    template_name = 'services/generate_jwt.html'
    form_class = GenerateJWTForm
    success_url = reverse_lazy('generate-jwt')

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            client_id=self.request.session['client_id'],
            secret=self.request.session['secret'],
        )
        if 'claims' in self.request.session:
            initial.update(self.request.session['claims'])

        return initial

    def form_valid(self, form):
        claims = {
            'scopes': form.cleaned_data['scopes'],
            'zaaktypes': form.cleaned_data['zaaktypes'],
        }

        auth = ClientAuth(
            client_id=form.cleaned_data['client_id'],
            secret=form.cleaned_data['secret'],
            **claims
        )

        self.request.session['claims'] = claims
        self.request.session['credentials'] = auth.credentials()
        return super().form_valid(form)
