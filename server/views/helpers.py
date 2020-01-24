from django.http import Http404

from server.models import Device

def device_from_token(token):
    device = Device.objects.filter(token=token).first()
    if not device:
        raise Http404('Token not valid')
    return device
