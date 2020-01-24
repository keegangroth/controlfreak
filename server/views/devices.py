from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render

from server.models import Device
from server.serializers import DeviceSerializer


class DeviceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Device.objects.all().order_by('-created_at')
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=True)
    def live(self, request, *args, **kwargs):
        device = self.get_object()#get_object_or_404(Device, pk=pk)
        context = {
            'logs': device.logs.all(),
            'credentials': device.credentials.all(),
        }
        return render(request, 'controlfreak/live_device.html', context)
