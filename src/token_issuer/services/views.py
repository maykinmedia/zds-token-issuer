from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from .forms import CreateCredentialsForm
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
