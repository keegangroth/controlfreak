import json

from django.http import JsonResponse, Http404, HttpResponseBadRequest

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from server.models import Credential
from server.views.helpers import device_from_token

@csrf_exempt
@require_http_methods(['POST'])
def credential(request):
    if request.headers['content-type'] != 'application/json':
        return HttpResponseBadRequest('Bad content-type, please use "application/json"')

    json_data = json.loads(request.body.decode("utf-8"))
    device = device_from_token(json_data.pop('token', None))

    if not __validate_request(json_data):
        return HttpResponseBadRequest('You must include non-empty target and user fields')

    credential = device.credentials.filter(target=json_data.get('target'), user=json_data.get('user')).first()
    if credential:
        credential.secret = json_data.get('secret', '')
        credential.save()
        return JsonResponse({})
    else:
        device.credentials.create(**json_data)
        return JsonResponse({}, status=201)

def __validate_request(json_data):
    for field in ['target', 'user']:
        if field not in json_data or not json_data[field]:
            return False

    return True
