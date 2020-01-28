'''View for the /credentials api'''

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from server.helpers import unauthorized
from server.models import Token
from server.serializers import CredentialSerializer

@api_view(['POST'])
@parser_classes([JSONParser])
def credential(request):
    '''Save the provided credential'''
    token = Token.objects.filter(token=request.data.pop('token', None)).first()
    if not token:
        return unauthorized()

    serializer = CredentialSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    _, created = token.device.credentials.update_or_create(target=request.data['target'],
                                                           user=request.data['user'],
                                                           defaults={'secret': request.data.get('secret', ''),
                                                                     'app': token.app})

    status = 201 if created else 200
    return Response({}, status=status)
