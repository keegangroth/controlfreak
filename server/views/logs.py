import json

from django.http import JsonResponse, HttpResponseBadRequest

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from server.models import Log
from server.views.helpers import device_from_token

@csrf_exempt
@require_http_methods(['POST'])
def log(request):
    if request.headers['content-type'] != 'application/json':
        return HttpResponseBadRequest('Bad content-type, please use "application/json"')

    json_data = json.loads(request.body.decode("utf-8"))
    device = device_from_token(json_data.pop('token', None))

    if not 'log' in json_data:
        return HttpResponseBadRequest('You must include a log')

    log = device.logs.first()
    if not log:
        log = device.logs.create(text=json_data['log'])
        log.save()
        return JsonResponse({}, status=201)

    log.text += json_data['log']
    log.save()
    return JsonResponse({})

@csrf_exempt
@require_http_methods(['POST'])
def clear(request):
    if request.headers['content-type'] != 'application/json':
        return HttpResponseBadRequest('Bad content-type, please use "application/json"')

    json_data = json.loads(request.body.decode("utf-8"))
    device = device_from_token(json_data.pop('token', None))

    log = device.logs.first()
    if log:
        log.delete()

    return JsonResponse({})
