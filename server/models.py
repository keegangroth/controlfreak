from django.db import models, IntegrityError


class ApplicationModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Device(ApplicationModel):
    token = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=['token']),
        ]
        unique_together = ['token']

    def create_device_ids(self, ids):
        for new_id in ids:
            # not as efficient as bulk_create, but actually runs the
            # validations...
            self.device_ids.create(**new_id)


class DeviceId(ApplicationModel):
    IdType = models.TextChoices('IdType', 'GOOGLE_AD_ID IOS_ID')
    id_type = models.CharField(choices=IdType.choices, max_length=100)
    value = models.CharField(max_length=100)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_ids')

    class Meta:
        indexes = [
            models.Index(fields=['id_type', 'value']),
        ]
        unique_together = [['id_type', 'value']]

    def validate_ids(sender, instance, **kwargs):
        # no idea what the point of empty=False is if it doesn't catch this...
        if not instance.value:
            raise IntegrityError('DeviceId value may not be empty')
        # seem like I shouldn't have to do this myself either...
        if instance.id_type not in sender.IdType:
            raise IntegrityError(
                'DeviceId type "{}" is not one of the permitted values: {}'.format(
                    instance.id_type,
                    ', '.join(sender.IdType)))

# I'd prefer a DB constraint, but this will have to do for now
models.signals.pre_save.connect(DeviceId.validate_ids, sender=DeviceId)


class Credential(ApplicationModel):
    target = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    secret = models.CharField(max_length=100)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='credentials')

    class Meta:
        indexes = [
            models.Index(fields=['target', 'user', 'device_id']),
        ]
        unique_together = [['target', 'user', 'device_id']]


class Log(ApplicationModel):
    text = models.TextField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
