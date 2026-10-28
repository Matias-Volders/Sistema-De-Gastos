import hashlib
import json
from decimal import Decimal
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.management import call_command, CommandError
from django.db import IntegrityError
from django.test import TestCase, override_settings
from werkzeug.security import generate_password_hash

from backend.finanzas import services
from backend.finanzas.models import Categoria, Egreso, Ingreso
from backend.usuarios.models import Usuario


class ImportacionTests(TestCase):
    password = "Importacion-Ficticia!123"

    def setUp(self):
        temporal = TemporaryDirectory(prefix="gastos-import-test-")
        self.addCleanup(temporal.cleanup)
        self.root = Path(temporal.name)
        self.origen = self.root / "datos"
        self.origen.mkdir()
        configuracion = override_settings(DATA_DIR=self.origen, LOCAL_DIR=self.root / "local")
        configuracion.enable()
        self.addCleanup(configuracion.disable)
        self.usuarios = [
            {"id": 7, "nombre": "Persona A", "email": "a@example.test", "password": make_password(self.password)},
            {"id": 9, "nombre": "Persona B", "email": "b@example.test", "password": generate_password_hash(self.password)},
        ]
        self.gastos = [
            {"id": 12, "user_id": 7, "monto": "25.50", "fecha": "2026-10-17", "descripcion": "Uno", "categoria": "Comida"},
            {"id": 14, "user_id": 7, "monto": 10.5, "fecha": "2026-09-17", "descripcion": "Dos", "categoria": "comida"},
            {"id": 15, "user_id": 9, "monto": "40.00", "fecha": "2026-10-17", "descripcion": "Tres", "categoria": "Comida"},
        ]
        self.ingresos = [
            {"id": 12, "user_id": 7, "monto": "100.00", "fecha": "2026-10-01", "descripcion": "Ingreso", "origen": "Trabajo"}
        ]
        self.escribir()

    def escribir(self):
        for nombre in ("usuarios", "gastos", "ingresos"):
            (self.origen / f"{nombre}.json").write_text(json.dumps(getattr(self, nombre)), encoding="utf-8")

    def ejecutar(self, *args):
        salida = StringIO()
        call_command("importar_json", *args, stdout=salida)
        return salida.getvalue()

    def cuentas(self):
        return tuple(modelo.objects.count() for modelo in (Usuario, Ingreso, Egreso, Categoria))

    def test_simulacion_es_predeterminada_y_no_escribe(self):
        antes = {p.name: p.read_bytes() for p in self.origen.iterdir()}
        self.assertIn("Simulación", self.ejecutar())
        self.assertEqual(self.cuentas(), (0, 0, 0, 0))
        self.assertFalse((self.root / "local/backups").exists())
        self.assertEqual(antes, {p.name: p.read_bytes() for p in self.origen.iterdir()})

    def test_importa_relaciones_conserva_ids_y_concilia_periodos(self):
        self.ejecutar("--aplicar")
        self.assertEqual(self.cuentas(), (2, 1, 3, 2))
        self.assertTrue(Ingreso.objects.filter(pk=12).exists())
        self.assertTrue(Egreso.objects.filter(pk=12).exists())
        self.assertEqual(services.calcular_balance(7)["balance"], Decimal("64.00"))
        self.assertEqual(services.calcular_balance(7, mes=10, anio=2026)["balance"], Decimal("74.50"))
        self.assertEqual(services.calcular_balance(9)["balance"], Decimal("-40.00"))
        self.assertEqual(Egreso.objects.get(pk=12).categoria_id, Egreso.objects.get(pk=14).categoria_id)

    def test_repetir_copia_identica_no_duplica(self):
        self.ejecutar("--aplicar")
        antes = self.cuentas()
        self.assertIn("usuarios=0, ingresos=0, egresos=0", self.ejecutar("--aplicar"))
        self.assertEqual(self.cuentas(), antes)

    def test_hashes_django_y_werkzeug_permiten_login(self):
        self.ejecutar("--aplicar")
        for email in ("a@example.test", "b@example.test"):
            usuario = authenticate(username=email, password=self.password)
            self.assertIsNotNone(usuario)
            usuario.refresh_from_db()
            self.assertFalse(usuario.password.startswith("werkzeug_legacy$"))

    def test_respaldo_es_copia_exacta_con_manifest(self):
        antes = {p.name: p.read_bytes() for p in self.origen.iterdir()}
        self.ejecutar("--aplicar")
        respaldo = next((self.root / "local/backups").iterdir())
        huellas = json.loads((respaldo / "manifest.json").read_text())
        for nombre, contenido in antes.items():
            self.assertEqual((respaldo / nombre).read_bytes(), contenido)
            self.assertEqual(huellas[nombre], hashlib.sha256(contenido).hexdigest())
            self.assertEqual((self.origen / nombre).read_bytes(), contenido)

    def test_error_durante_carga_revierte_todas_las_tablas(self):
        with patch("backend.core.importacion.Egreso.objects.create", side_effect=IntegrityError("fallo simulado")):
            with self.assertRaises(CommandError):
                self.ejecutar("--aplicar")
        self.assertEqual(self.cuentas(), (0, 0, 0, 0))
        self.assertTrue((self.root / "local/backups").exists())

    def test_respaldo_inaccesible_impide_escritura(self):
        with patch("backend.core.legacy.DatosAnteriores.respaldar", side_effect=OSError("simulado")):
            with self.assertRaises(CommandError):
                self.ejecutar("--aplicar")
        self.assertEqual(self.cuentas(), (0, 0, 0, 0))

    def test_conflicto_de_correo_no_sobrescribe_ni_importa(self):
        Usuario.objects.create(id=50, email="a@example.test", nombre="Existente", password="!inutilizable")
        with self.assertRaises(CommandError):
            self.ejecutar("--aplicar")
        self.assertEqual(self.cuentas(), (1, 0, 0, 0))
        self.assertEqual(Usuario.objects.get(pk=50).nombre, "Existente")

    def test_registro_editado_no_se_sobrescribe_al_reimportar(self):
        self.ejecutar("--aplicar")
        Ingreso.objects.filter(pk=12).update(monto=200)
        with self.assertRaises(CommandError):
            self.ejecutar("--aplicar")
        self.assertEqual(Ingreso.objects.get(pk=12).monto, Decimal("200"))

    def test_archivo_corrupto_o_ausente_no_se_interpreta_como_vacio(self):
        ruta = self.origen / "gastos.json"
        ruta.write_text("incompleto", encoding="utf-8")
        with self.assertRaises(CommandError):
            self.ejecutar("--aplicar")
        self.assertEqual(ruta.read_text(), "incompleto")
        ruta.unlink()
        with self.assertRaises(CommandError):
            self.ejecutar("--aplicar")
        self.assertEqual(self.cuentas(), (0, 0, 0, 0))

    def test_datos_invalidos_y_huerfanos_no_escriben(self):
        original = self.gastos[0].copy()
        for cambio in ({"user_id": 100}, {"id": True}, {"monto": "NaN"},
                       {"fecha": "2025-02-29"}, {"campo_nuevo": "no ignorar"},
                       {"categoria": " "}, {"id": 14}):
            self.gastos[0] = {**original, **cambio}
            self.escribir()
            with self.assertRaises(CommandError):
                self.ejecutar("--aplicar")
            self.assertEqual(self.cuentas(), (0, 0, 0, 0))

    def test_secuencias_permiten_altas_despues_de_importar(self):
        self.ejecutar("--aplicar")
        usuario = Usuario.objects.create_user(nombre="Nuevo", email="nuevo@example.test", password=self.password)
        self.assertGreater(usuario.pk, 9)
        for tipo, minimo in (("gastos", 15), ("ingresos", 12)):
            campos = {
                "monto": "1.00", "fecha": "2026-10-20", "descripcion": "Posterior",
                "categoria" if tipo == "gastos" else "origen": "Nuevo",
            }
            self.assertGreater(services.guardar_movimiento(tipo, 7, campos)["id"], minimo)

    def test_copia_respaldada_permite_reconstruir_en_base_vacia(self):
        self.ejecutar("--aplicar")
        respaldo = next((self.root / "local/backups").iterdir())
        esperado = services.calcular_balance(7)
        Egreso.objects.all().delete()
        Ingreso.objects.all().delete()
        Categoria.objects.all().delete()
        Usuario.objects.all().delete()
        self.ejecutar("--origen", str(respaldo), "--aplicar")
        self.assertEqual(services.calcular_balance(7), esperado)
        self.assertEqual(self.cuentas(), (2, 1, 3, 2))
