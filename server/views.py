from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404

from server.models import Device

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def health(request):
    return JsonResponse({'hello':'world'})

#def register(request):
#    return HttpResponse(status=201)

def devices(request):
    # why JsonResponse doesn't handle models and querysets idk!
    devices = list(Device.objects.all().values())
    return JsonResponse({'devices': devices})

def device(request, device_id):
    try:
        d = Device.objects.filter(pk=device_id).values()[0]
    except Device.DoesNotExist:
        raise Http404("Device does not exist")
    return JsonResponse({'device': d})
