from django.urls import path

from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('health', views.health, name='health'),
    path('devices', views.devices, name='devices'),
    path('devices/<int:device_id>', views.device, name='device'),
]
