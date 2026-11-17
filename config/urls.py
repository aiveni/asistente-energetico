"""Rutas generales: administración de Django y entrada de la app de energía."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("energia.urls")),
]
