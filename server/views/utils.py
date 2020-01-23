from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def health(request):
    return JsonResponse({'hello':'world'})
