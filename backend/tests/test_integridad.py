from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal

from django.db import connection, close_old_connections, DatabaseError, IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TransactionTestCase
from django.test.utils import CaptureQueriesContext

from backend.finanzas import services
from backend.finanzas.models import Categoria, Egreso, Ingreso
from backend.tests.base import BaseDatosTestCase
from backend.usuarios.models import Usuario


class IntegridadTests(BaseDatosTestCase):
    def test_cuatro_entidades_sin_tabla_movimiento(self):
        tablas = set(connection.introspection.table_names())
        self.assertTrue({"usuario", "ingreso", "egreso", "categoria"}.issubset(tablas))
        self.assertFalse({"movimiento", "cuenta"}.intersection(tablas))

    def test_monto_invalido_rechazado_incluso_sin_formulario(self):
        for monto in (Decimal("0"), Decimal("-1"), Decimal("NaN"), Decimal("1000000000000")):
            with self.assertRaises(DatabaseError), transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO ingreso (usuario_id, monto, fecha, descripcion, origen, creado_en, actualizado_en) "
                        "VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                        [self.uno.pk, monto, date(2026, 1, 1), "Prueba", "Trabajo"],
                    )

    def test_categoria_ajena_rechazada_por_postgresql(self):
        categoria = Categoria.objects.create(usuario=self.dos, nombre="Privada")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Egreso.objects.create(usuario=self.uno, categoria=categoria, monto=10, fecha=date(2026, 1, 1), descripcion="Prueba")

    def test_categoria_utilizada_y_usuario_no_se_borran_en_cascada(self):
        services.guardar_movimiento("gastos", 1, self.datos_movimiento())
        categoria = Categoria.objects.get(usuario_id=1)
        with self.assertRaises(ProtectedError):
            categoria.delete()
        with self.assertRaises(ProtectedError):
            self.uno.delete()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Categoria.objects.filter(pk=categoria.pk).update(usuario=self.dos)

    def test_correo_unico_sin_distinguir_mayusculas_en_sql(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Usuario.objects.create(email="UNO@EXAMPLE.TEST", nombre="Otra", password="!inutilizable")

    def test_listado_con_categorias_no_hace_una_consulta_por_fila(self):
        for numero in range(4):
            services.guardar_movimiento("gastos", 1, self.datos_movimiento(categoria=f"Categoria {numero}"))
        with self.assertNumQueries(1):
            self.assertEqual(len(services.listar_movimientos("gastos", 1)), 4)

    def test_balance_agrega_en_una_sentencia_y_total_filtra_en_sql(self):
        services.guardar_movimiento("ingresos", 1, self.datos_movimiento("ingresos", monto="100"))
        services.guardar_movimiento("gastos", 1, self.datos_movimiento())
        services.guardar_movimiento("gastos", 2, self.datos_movimiento(monto="999"))
        with CaptureQueriesContext(connection) as consultas:
            self.assertEqual(services.calcular_balance(1, mes=10, anio=2026)["balance"], Decimal("74.50"))
        self.assertEqual(len(consultas), 1)
        self.assertIn("SUM(", consultas[0]["sql"])
        with CaptureQueriesContext(connection) as consultas:
            self.assertEqual(services.total_movimientos("gastos", 1, mes=10, anio=2026), Decimal("25.50"))
        self.assertEqual(len(consultas), 1)
        self.assertIn("SUM(", consultas[0]["sql"])
        self.assertIn("WHERE", consultas[0]["sql"])

    def test_periodos_extremos_no_desbordan_la_fecha(self):
        for anio in (1, 9999):
            services.guardar_movimiento("ingresos", 1, self.datos_movimiento("ingresos", fecha=date(anio, 12, 31)))
            self.assertEqual(services.calcular_balance(1, mes=12, anio=anio)["total_ingresos"], Decimal("25.50"))


class ConcurrenciaTests(TransactionTestCase):
    reset_sequences = True

    def test_altas_simultaneas_no_duplican_categoria_ni_pierden_registros(self):
        usuario = Usuario.objects.create_user(nombre="Concurrente", email="concurrente@example.test", password="Temporal!12345")

        def crear(numero):
            close_old_connections()
            try:
                return services.guardar_movimiento("gastos", usuario.pk, {
                    "monto": "25.50", "fecha": "2026-10-17", "descripcion": f"Prueba {numero}", "categoria": "Comida",
                })["id"]
            finally:
                connection.close()

        with ThreadPoolExecutor(max_workers=4) as executor:
            ids = list(executor.map(crear, range(12)))
        self.assertEqual(len(set(ids)), 12)
        self.assertEqual(Categoria.objects.count(), 1)
        self.assertEqual(Egreso.objects.count(), 12)
        self.assertEqual(services.total_movimientos("gastos", usuario.pk), Decimal("306.00"))
