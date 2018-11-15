from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import Service, Configuration


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('label', 'api_root')


admin.site.register(Configuration, SingletonModelAdmin)
