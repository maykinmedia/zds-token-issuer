from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from .forms import CreateCredentialsForm
from .models import Service


class CreateCredentialsView(SuccessMessageMixin, FormView):
    template_name = 'index.html'
    form_class = CreateCredentialsForm
    success_message = _("Your credentials have been registered with the services")
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        client_id, secret = form.save()

        for service in Service.objects.iterator():
            service.register_client(client_id, secret)

        return super().form_valid(form)
