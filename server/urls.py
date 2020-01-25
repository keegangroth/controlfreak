from django.urls import include, path, re_path
from rest_framework import routers

import server.views as views

router = routers.DefaultRouter()
router.register(r'devices', views.devices.DeviceViewSet)

urlpatterns = [
    path('', views.utils.index),
    re_path('^health/?$', views.utils.health),

    path('', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),

    re_path(r'^register/?$', views.register.register),
    re_path(r'^credentials/?$', views.credentials.credential),
    re_path(r'^logs/?$', views.logs.logs),
    re_path(r'^logs/clear/?$', views.logs.clear),
]
