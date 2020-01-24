from django.urls import path, re_path

import server.views as views

urlpatterns = [
    path('', views.utils.index),
    path('health/', views.utils.health),

    path('devices/', views.device.devices),
    path('devices/<int:device_id>/', views.device.device),
    path('devices/<int:device_id>/live/', views.device.live_device),

    re_path(r'register/?$', views.device.register),
    re_path(r'credentials/?$', views.credentials.credential),
    re_path(r'logs/?$', views.logs.log),
    re_path(r'logs/clear/?$', views.logs.clear),
]
