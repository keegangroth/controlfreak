'''View for the /register api'''

import uuid
from functools import reduce

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q

from server.models import Device, DeviceId, App
from server.serializers import DeviceIdSerializer


@api_view(['POST'])
@parser_classes([JSONParser])
def register(request):
    '''Register a device

    Given a set of device identifiers, find or create a device and
    return the token for it.
    '''
    app = App.objects.filter(api_key=request.data.get('app_guid')).first()
    if not app:
        return Response({'detail': 'Authentication credentials were not provided.'}, status=403)

    request_ids = []
    if 'id_type' in request.data:
        request_ids += [DeviceIdSerializer(data=request.data)]
    if 'device_ids' in request.data:
        request_ids += [DeviceIdSerializer(data=d) for d in request.data['device_ids']]

    if not request_ids:
        return Response({'device_ids': 'This field is required'}, status=400)

    for request_id in request_ids:
        if not request_id.is_valid():
            return Response({'device_ids': request_id.errors}, status=400)

    status = 200

    id_filter = reduce(lambda x, y: x | y, [Q(**d.data) for d in request_ids])
    device_id = DeviceId.objects.filter(id_filter).first()
    if device_id:
        # handle multiple matching devices?
        # add/update device ids?
        device = device_id.device
    else:
        try:
            with transaction.atomic():
                device = Device.objects.create()
                device.create_device_ids([d.data for d in request_ids])
            status = 201
        except IntegrityError as ex:
            return Response({'errors': [str(ex)]}, status=400)

    token, _ = device.tokens.get_or_create(app_id=app.pk,
                                           defaults={'token': uuid.uuid4().hex})

    return Response({'token': token.token, 'id': device.pk}, status=status)
