from unittest.mock import patch

from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import OperationalError
from django.test import Client
from werkzeug.security import generate_password_hash

from backend.tests.base import BaseDatosTestCase
from backend.usuarios import repository, services
from backend.usuarios.models import Usuario


class UsuariosTests(BaseDatosTestCase):
    def test_registro_directo_valida_y_no_crea_filas_invalidas(self):
        for nombre, email, password in (
            ("", "nueva@example.test", self.password),
            ("Nueva", "incorrecto", self.password),
            ("Nueva", "nueva@example.test", "x"),
            ("Nueva", "UNO@EXAMPLE.TEST", self.password),
        ):
            with self.assertRaises(ValidationError):
                services.registrar_usuario(nombre, email, password)
            self.assertEqual(Usuario.objects.count(), 2)

    def test_paginas_publicas_y_privadas(self):
        for url in ("/", "/registro", "/iniciarSesion"):
            self.assertEqual(self.client.get(url).status_code, 200)
        for url in ("/panel", "/gastos", "/ingresos", "/balance", "/gastos/editar/1"):
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_registro_login_logout_y_last_login_persistidos(self):
        self.assertEqual(self.client.post("/registro", {
            "nombre": "Nueva Persona", "email": "NUEVA@example.test",
            "password": self.password, "confirmar_password": self.password,
        }).status_code, 302)
        usuario = repository.por_email("nueva@example.test")
        self.assertNotEqual(usuario.password, self.password)
        self.assertIsNone(usuario.last_login)
        self.assertEqual(self.login(email="NUEVA@example.test").status_code, 302)
        usuario.refresh_from_db()
        self.assertIsNotNone(usuario.last_login)
        self.assertContains(self.client.get("/panel"), "Nueva Persona")
        self.assertRedirects(self.client.get("/"), "/panel")
        self.assertEqual(self.client.get("/cerrarSesion").status_code, 405)
        self.assertEqual(self.client.post("/cerrarSesion").status_code, 302)
        self.assertEqual(self.client.get("/panel").status_code, 302)

    def test_registro_rechaza_correo_clave_confirmacion_y_duplicados(self):
        for cambios in ({"email": "invalido"}, {"password": "x", "confirmar_password": "x"},
                        {"confirmar_password": "distinta"}, {"email": "UNO@EXAMPLE.TEST"}):
            response = self.client.post("/registro", {
                "nombre": "Nueva", "email": "nueva@example.test", "password": self.password,
                "confirmar_password": self.password, **cambios,
            })
            self.assertTrue(response.context["form"].errors)
            self.assertEqual(Usuario.objects.count(), 2)

    def test_password_con_espacios_no_se_recorta(self):
        password = " " + self.password + " "
        services.registrar_usuario("Espacios", "espacios@example.test", password)
        self.assertIsNotNone(authenticate(username="espacios@example.test", password=password))
        self.assertIsNone(authenticate(username="espacios@example.test", password=password.strip()))

    def test_password_similar_a_nombre_o_correo(self):
        for password in ("persona@example.test", "NombreApellidoDistintivo"):
            response = self.client.post("/registro", {
                "nombre": "NombreApellidoDistintivo", "email": "persona@example.test",
                "password": password, "confirmar_password": password,
            })
            self.assertIn("password", response.context["form"].errors)

    def test_hash_werkzeug_se_actualiza_al_login_y_la_sesion_sigue_valida(self):
        anterior = "werkzeug_legacy$" + generate_password_hash(self.password)
        Usuario.objects.filter(pk=1).update(password=anterior)
        self.assertEqual(self.login().status_code, 302)
        self.uno.refresh_from_db()
        self.assertNotEqual(self.uno.password, anterior)
        self.assertTrue(self.uno.check_password(self.password))
        self.assertEqual(self.client.get("/panel").status_code, 200)
        self.assertEqual(self.client.get("/panel").status_code, 200)

    def test_login_invalido_no_crea_sesion(self):
        for email in ("uno@example.test", "inexistente@example.test"):
            self.assertContains(self.login(email=email, password="equivocada"), "Correo o contraseña incorrectos.")
            self.assertEqual(self.client.get("/panel").status_code, 302)

    def test_cuenta_inactiva_no_ingresa(self):
        Usuario.objects.filter(pk=1).update(is_active=False)
        self.assertIsNone(authenticate(username="uno@example.test", password=self.password))

    def test_sesion_persiste_en_otro_cliente_y_logout_la_invalida(self):
        self.login()
        nuevo = Client()
        nuevo.cookies = self.client.cookies.copy()
        self.assertEqual(nuevo.get("/panel").status_code, 200)
        self.client.post("/cerrarSesion")
        self.assertEqual(nuevo.get("/panel").status_code, 302)

    def test_usuario_eliminado_pierde_acceso(self):
        self.login()
        self.uno.delete()
        self.assertEqual(self.client.get("/panel").status_code, 302)

    def test_password_modificado_invalida_sesion(self):
        self.login()
        Usuario.objects.filter(pk=1).update(password="!password-inutilizable")
        self.assertEqual(self.client.get("/panel").status_code, 302)

    def test_csrf_registro_login_logout(self):
        cliente = Client(enforce_csrf_checks=True)
        self.assertEqual(cliente.post("/registro", {}).status_code, 403)
        self.assertEqual(self.login(client=cliente).status_code, 403)
        cliente.get("/iniciarSesion")
        token = cliente.cookies["csrftoken"].value
        self.assertEqual(cliente.post("/iniciarSesion", {
            "email": "uno@example.test", "password": self.password, "csrfmiddlewaretoken": token,
        }).status_code, 302)
        self.assertEqual(cliente.post("/cerrarSesion").status_code, 403)
        self.assertEqual(cliente.post("/cerrarSesion", {
            "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value,
        }).status_code, 302)

    def test_nombre_se_escapa_en_html(self):
        Usuario.objects.filter(pk=1).update(nombre="<script>alert(1)</script>")
        self.login()
        response = self.client.get("/panel")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_error_de_conexion_se_muestra_sin_detalles_privados(self):
        with patch("backend.usuarios.models.UsuarioManager.get_by_natural_key",
                   side_effect=OperationalError("detalle privado simulado")):
            response = self.login()
        self.assertEqual(response.status_code, 503)
        self.assertNotContains(response, "detalle privado", status_code=503)
