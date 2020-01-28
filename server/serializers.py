'''Serializers for our models'''

from rest_framework import serializers
from server.models import Credential, Device, DeviceId, Log, Token


class DeviceIdSerializer(serializers.ModelSerializer):
    '''Serializer for DeviceId'''
    class Meta:
        model = DeviceId
        fields = ['value', 'id_type']

    def get_unique_together_validators(self):
        '''Overriding method to disable unique together checks'''
        return []


class CredentialSerializer(serializers.ModelSerializer):
    '''Serializer for Credential'''
    app = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Credential
        fields = ['app', 'target', 'user', 'secret']


class LogSerializer(serializers.ModelSerializer):
    '''Serializer for Log'''
    app = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Log
        fields = ['app', 'text']


class TokenSerializer(serializers.ModelSerializer):
    '''Serializer for Token'''
    app = serializers.SlugRelatedField(read_only=True, slug_field='name')

    class Meta:
        model = Token
        fields = ['app', 'token']


class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    '''Serializer for Device'''
    device_ids = DeviceIdSerializer(many=True, read_only=True)
    logs = LogSerializer(many=True, read_only=True)
    credentials = CredentialSerializer(many=True, read_only=True)
    tokens = TokenSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = '__all__'
