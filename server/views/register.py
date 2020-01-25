import uuid
from functools import reduce

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q

from server.models import Device, DeviceId
from server.serializers import DeviceIdSerializer


@api_view(['POST'])
@parser_classes([JSONParser])
def register(request):
    request_ids = []
    if 'id_type' in request.data:
        request_ids += [DeviceIdSerializer(data=request.data)]
    if 'device_ids' in request.data:
        request_ids += [DeviceIdSerializer(data=d) for d in request.data['device_ids']]

    if not request_ids:
        return Response({'device_ids': 'This field is required'}, status=400)

    for request_id in request_ids:
        if not request_id.is_valid():
            return Response(request_id.errors, status=400)

    id_filter = reduce(lambda x, y: x | y, [Q(**d.data) for d in request_ids])
    device_id = DeviceId.objects.filter(id_filter).first()
    if device_id:
        # todo: handle multiple matching devices?
        # todo: add/update device ids?
        return Response({'token': device_id.device.token,
                         'id': device_id.device.pk})

    try:
        with transaction.atomic():
            device = Device.objects.create(token=uuid.uuid4().hex)
            device.create_device_ids([d.data for d in request_ids])
    except IntegrityError as ex:
        return Response({'errors': [str(ex)]}, status=400)

    return Response({'token': device.token, 'id': device.pk}, status=201)
