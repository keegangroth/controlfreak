'''Shared helper methods'''

from rest_framework.response import Response


def unauthorized():
    '''Return an unauthorized/403 response'''
    return Response({'detail': 'Authentication credentials were not provided.'}, status=403)
