from django.contrib import admin

from . import models


class DeviceIdInline(admin.TabularInline):
    model = models.DeviceId
    extra = 0
    readonly_fields = ('id_type', 'value')
    can_delete = False

class CredentialInline(admin.TabularInline):
    model = models.Credential
    extra = 0

class LogInline(admin.TabularInline):
    model = models.Log
    extra = 0

class DeviceAdmin(admin.ModelAdmin):
    inlines = [
        DeviceIdInline,
        CredentialInline,
        LogInline,
    ]


admin.site.register(models.Device, DeviceAdmin)
admin.site.register(models.DeviceId)
admin.site.register(models.Credential)
admin.site.register(models.Log)
