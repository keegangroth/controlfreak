'''Configuration for the django admin console.'''

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from . import models


class DeviceIdInline(admin.TabularInline):
    '''DeviceId inline for display in Device'''

    model = models.DeviceId
    extra = 0
    readonly_fields = ('id_type', 'value')
    can_delete = False

class CredentialInline(admin.TabularInline):
    '''Credential inline for display in Device'''

    model = models.Credential
    extra = 0

class LogInline(admin.TabularInline):
    '''Log inline for display in Device'''

    model = models.Log
    extra = 0

class DeviceAdmin(admin.ModelAdmin):
    '''Admin view for Device'''

    inlines = [
        DeviceIdInline,
        CredentialInline,
        LogInline,
    ]

class DeviceIdAdmin(admin.ModelAdmin):
    '''Admin view for DeviceId'''

    @staticmethod
    def device_link(obj):
        '''Make a link to the associated device since that's what we really
        care about'''
        url = reverse('admin:server_device_change', args=[obj.device.id])
        return format_html("<a href='{}'>{}</a>", url, obj.device)

    device_link.admin_order_field = 'device'
    device_link.short_description = 'device'

    search_fields = ('value',)
    list_display = ('device_link', 'value', 'id_type')

admin.site.register(models.Device, DeviceAdmin)
admin.site.register(models.DeviceId, DeviceIdAdmin)
