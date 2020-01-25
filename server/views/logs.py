from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from server.models import Log, Device


@api_view(['POST'])
@parser_classes([JSONParser])
def log(request, format=None):
    device = get_object_or_404(Device, token=request.data.pop('token', None))

    try:
        text = request.data['log']
    except KeyError:
        return Response({'log': 'This field is required'}, status=400)

    log = device.logs.first()
    if log:
        log.text += text
        log.save()
        return Response({})

    log = device.logs.create(text=text)
    return Response({}, status=201)

@api_view(['POST'])
@parser_classes([JSONParser])
def clear(request, format=None):
    device = get_object_or_404(Device, token=request.data.pop('token', None))

    log = device.logs.first()
    if log:
        log.delete()

    return Response({})
