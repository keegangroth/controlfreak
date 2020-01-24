import json
import uuid
from functools import reduce

from django.http import JsonResponse, HttpResponseBadRequest

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from django.db import IntegrityError
from django.db.models import Q
from server.models import Device, DeviceId

@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    json_device_ids = __device_ids(request)
    if not json_device_ids:
        return HttpResponseBadRequest('You must supply device ids')

    id_filter = reduce(lambda x, y: x | y, [Q(**d) for d in json_device_ids])
    device_id = DeviceId.objects.filter(id_filter).first()
    if device_id:
        # todo: handle multiple matching devices?
        # todo: add/update device ids?
        return JsonResponse({'token': device_id.device.token,
                             'id': device_id.device.pk})

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

    return JsonResponse({'token': device.token, 'id': device.pk}, status=201)

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
