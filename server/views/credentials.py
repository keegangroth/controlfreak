'''View for the /credentials api'''

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from server.models import Device
from server.serializers import CredentialSerializer

@api_view(['POST'])
@parser_classes([JSONParser])
def credential(request):
    '''Save the provided credential'''
    device = get_object_or_404(Device, token=request.data.pop('token', None))

    serializer = CredentialSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    _, created = device.credentials.update_or_create(target=request.data['target'],
                                                     user=request.data['user'],
                                                     defaults={'secret': request.data.get('secret', '')})

    status = 201 if created else 200
    return Response({}, status=status)
