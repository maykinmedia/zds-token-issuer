from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import Configuration


@admin.register(Configuration)
class ConfigurationAdmin(SingletonModelAdmin):
    pass
