'''View for the /logs apis'''

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from server.helpers import unauthorized
from server.models import Log, Token


@api_view(['POST'])
@parser_classes([JSONParser])
def logs(request):
    '''Save the provided log'''
    token = Token.objects.filter(token=request.data.pop('token', None)).first()
    if not token:
        return unauthorized()

    try:
        text = request.data['log']
    except KeyError:
        return Response({'log': 'This field is required'}, status=400)

    log = Log.objects.filter(device=token.device, app=token.app).first()
    if log:
        log.text += text
        log.save()
        return Response({})

    log = Log.objects.create(text=text, device=token.device, app=token.app)
    return Response({}, status=201)

@api_view(['POST'])
@parser_classes([JSONParser])
def clear(request):
    '''Delete a log for the identified device'''
    token = Token.objects.filter(token=request.data.pop('token', None)).first()
    if not token:
        return unauthorized()

    log = Log.objects.filter(device=token.device, app=token.app).first()
    if log:
        log.delete()

    return Response({})
