from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from server.models import Device, DeviceId

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def devices(request):
    if request.method == 'GET':
        return __all()
    elif request.method == 'POST':
        return __post(request)

@require_http_methods(['GET', 'PUT', 'PATCH'])
def device(request, device_id):
    if request.method == 'GET':
        return __get(device_id)
    else:
        return __put(request, device_id)

def __all():
    # why JsonResponse doesn't handle models and querysets idk!
    devices = list(Device.objects.all().values())
    for d in devices:
        device_ids = list(DeviceId.objects.filter(device=d['id']).values())
        d.update(device_ids=device_ids)
    return JsonResponse({'devices': devices})

def __get(device_id):
    result = Device.objects.filter(pk=device_id)
    if not result:
        raise Http404("Device does not exist")
    d = result.values()[0]
    device_ids = list(DeviceId.objects.filter(device=d['id']).values())
    d.update(device_ids=device_ids)
    return JsonResponse({'device': d})

def __post(request):
    return JsonResponse({})

def __put(request, device_id):
    pass
