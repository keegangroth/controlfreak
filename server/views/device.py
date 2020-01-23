import json
import uuid

from functools import reduce

from django.http import JsonResponse, Http404, HttpResponseBadRequest

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.db import IntegrityError
from django.db.models import Q
from server.models import Device, DeviceId

@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    return __post(request)

@require_http_methods(['GET'])
def devices(request):
    return __all()

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
    d.update(device_ids=list(result.first().device_ids.values()))
    d.update(credentials=list(result.first().credentials.values()))
    return JsonResponse({'device': d})

def __post(request):
    if request.headers['content-type'] != 'application/json':
        return HttpResponseBadRequest('Bad content-type, please use "application/json"')

    json_device_ids = __device_ids(request)
    if not json_device_ids:
        return HttpResponseBadRequest('You must supply device ids')

    id_filter = reduce(lambda x, y: x | y, [Q(**d) for d in json_device_ids])
    device_id = DeviceId.objects.filter(id_filter).first()
    if device_id:
        # todo: handle multiple matching devices?
        # todo: add/update device ids?
        return JsonResponse({'token': device_id.device.token})

    try:
        device = Device(token=uuid.uuid4().hex)
        device.save()
        device.create_device_ids(json_device_ids)
    except Exception as ex:
        if device:
            device.delete()

        if type(ex) is IntegrityError:
            return HttpResponseBadRequest(str(ex))
        else:
            raise(ex)

    return JsonResponse({'token': device.token}, status=201)

def __put(request, device_id):
    pass

def __device_ids(request):
    json_data = json.loads(request.body.decode("utf-8"))
    if not (('device_ids' in json_data and json_data['device_ids'])
            or ('id_type' in json_data and 'value' in json_data)):
        return None
    if 'device_ids' in json_data:
        return json_data['device_ids']
    else:
        json_data.pop('app_guid', None)
        return [json_data]
