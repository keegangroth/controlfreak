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


class TokenInline(admin.TabularInline):
    '''Token inline for display in Device'''
    model = models.Token
    extra = 0
    can_delete = False
    exclude = ['app']

    @staticmethod
    def app_name(instance):
        '''Return the name of the associated app'''
        return instance.app.name if instance.app else ''

    readonly_fields = ('app_name', 'token')

    @staticmethod
    def has_change_permission(request, obj=None):
        '''Do not allow any edits to tokens'''
        return False


class AppTokenInline(admin.TabularInline):
    '''Token inline for display in App'''
    model = models.Token
    extra = 0
    exclude = ['device']

    @staticmethod
    def device_link(obj):
        '''Make a link to the associated device since that's what we really
        care about'''
        url = reverse('admin:server_device_change', args=[obj.device.id])
        return format_html("<a href='{}'>{}</a>", url, obj.device)

    device_link.admin_order_field = 'device'
    device_link.short_description = 'device'

    readonly_fields = ('device_link', 'token')

    @staticmethod
    def has_add_permission(request, obj=None):
        '''Do not allow creates of new tokens'''
        return False


class CredentialInline(admin.TabularInline):
    '''Credential inline for display in Device'''
    model = models.Credential
    extra = 0
    exclude = ['app']

    @staticmethod
    def app_name(instance):
        '''Return the name of the associated app'''
        return instance.app.name if instance.app else ''

    readonly_fields = ('app_name',)

class LogInline(admin.TabularInline):
    '''Log inline for display in Device'''
    model = models.Log
    extra = 0
    exclude = ['app']

    @staticmethod
    def app_name(instance):
        '''Return the name of the associated app'''
        return instance.app.name if instance.app else ''

    readonly_fields = ('app_name',)


class AppAdmin(admin.ModelAdmin):
    '''Admin view for App'''
    search_fields = ('name', 'api_key')
    list_display = ('name', 'api_key')
    inlines = [AppTokenInline]


class DeviceAdmin(admin.ModelAdmin):
    '''Admin view for Device'''
    inlines = [
        CredentialInline,
        DeviceIdInline,
        LogInline,
        TokenInline,
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


admin.site.register(models.App, AppAdmin)
admin.site.register(models.Device, DeviceAdmin)
admin.site.register(models.DeviceId, DeviceIdAdmin)
