from django.urls import path

import server.views as views

urlpatterns = [
    path('index', views.utils.index),
    path('health', views.utils.health),
    path('register', views.device.register),
    path('devices', views.device.devices),
    path('devices/<int:device_id>', views.device.device),
    path('devices/<int:device_id>/live', views.device.live_device),
    path('credentials', views.credentials.credential),
    path('logs', views.logs.log),
    path('logs/clear', views.logs.clear),
]
