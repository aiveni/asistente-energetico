"""Asocia la entrada de la aplicación con la vista del formulario."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
]
