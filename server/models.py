from django.db import models

class ApplicationModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Device(ApplicationModel):
    token = models.CharField(max_length=100)


class DeviceId(ApplicationModel):
    IdType = models.TextChoices('IdType', 'GOOGLE_AD_ID IOS_ID')
    id_type = models.CharField(choices=IdType.choices, max_length=100)
    value = models.CharField(max_length=100)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_ids')
