from django.contrib.auth import get_user_model
from django.core.management.color import no_style
from django.db import connection
from django.test import TestCase


class BaseDatosTestCase(TestCase):
    """Django crea una base test_ y revierte cada prueba; nunca usa los JSON."""
    password = "Prueba-Temporal!839"

    @classmethod
    def setUpTestData(cls):
        usuario = get_user_model()
        cls.uno = usuario.objects.create_user(
            id=1, nombre="Persona Uno", email="uno@example.test", password=cls.password
        )
        cls.dos = usuario.objects.create_user(
            id=2, nombre="Persona Dos", email="dos@example.test", password=cls.password
        )
        with connection.cursor() as cursor:
            for sentencia in connection.ops.sequence_reset_sql(no_style(), [usuario]):
                cursor.execute(sentencia)

    def login(self, client=None, email="uno@example.test", password=None):
        return (client or self.client).post(
            "/iniciarSesion", {"email": email, "password": password or self.password}
        )

    def datos_movimiento(self, tipo="gastos", **cambios):
        datos = {
            "monto": "25.50", "fecha": "2026-10-17", "descripcion": "Prueba",
            "categoria" if tipo == "gastos" else "origen": "Comida" if tipo == "gastos" else "Trabajo",
        }
        datos.update(cambios)
        return datos

    def estado(self, tipo):
        from backend.finanzas.repository import obtener_modelo
        return list(obtener_modelo(tipo).objects.order_by("pk").values())
