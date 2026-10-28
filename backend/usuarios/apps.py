from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    name = "backend.usuarios"
    # Se conserva la señal estándar: last_login ahora se guarda mediante ORM.
