from server.models import Device, DeviceId, Credential
from rest_framework import serializers

class DeviceIdSerializer(serializers.ModelSerializer):
     class Meta:
        model = DeviceId
        fields = ['value', 'id_type']


class CredentialSerializer(serializers.ModelSerializer):
     class Meta:
        model = Credential
        fields = ['target', 'user', 'secret']


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    device_ids = DeviceIdSerializer(many=True, read_only=True)
    logs = serializers.SlugRelatedField(many=True, read_only=True, slug_field='text')
    credentials = CredentialSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = '__all__'

