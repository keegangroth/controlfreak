'''Serializers for our models'''

from rest_framework import serializers
from server.models import Device, DeviceId, Credential


class DeviceIdSerializer(serializers.ModelSerializer):
    '''Serializer for DeviceId.'''

    class Meta:
        model = DeviceId
        fields = ['value', 'id_type']

    def get_unique_together_validators(self):
        '''Overriding method to disable unique together checks'''
        return []


class CredentialSerializer(serializers.ModelSerializer):
    '''Serializer for Credential.'''

    class Meta:
        model = Credential
        fields = ['target', 'user', 'secret']


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    '''Serializer for Device.'''

    device_ids = DeviceIdSerializer(many=True, read_only=True)
    logs = serializers.SlugRelatedField(many=True, read_only=True, slug_field='text')
    credentials = CredentialSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = '__all__'
