'''Views for the /deviecs apis'''

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render

from server.models import Device
from server.serializers import DeviceSerializer


class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    '''View set supply read-only access to the devices table'''

    queryset = Device.objects.all().order_by('-created_at')
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=True)
    def live(self, request, *_args, **_kwargs):
        '''Simple view that automatically refreshes the page'''
        device = self.get_object()
        context = {
            'logs': device.logs.all(),
            'credentials': device.credentials.all(),
        }
        return render(request, 'controlfreak/live_device.html', context)
