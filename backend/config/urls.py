from django.urls import include, path

urlpatterns = [
    path("", include("backend.usuarios.urls")),
    path("", include("backend.finanzas.urls")),
]
