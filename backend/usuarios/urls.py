from django.urls import path
from backend.usuarios import views

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("registro", views.registro, name="registro"),
    path("iniciarSesion", views.iniciar_sesion, name="iniciar_sesion"),
    path("cerrarSesion", views.cerrar_sesion, name="cerrar_sesion"),
    path("panel", views.panel, name="panel"),
]
