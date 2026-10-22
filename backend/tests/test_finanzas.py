from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import Client

from backend.finanzas import services
from backend.finanzas.exceptions import MovimientoNoEncontrado
from backend.tests.base import BaseDatosTestCase


class FinanzasTests(BaseDatosTestCase):
    def setUp(self):
        super().setUp()
        self.login()

    def test_servicios_devuelven_tipos_python_y_rechazan_movimientos_ajenos(self):
        for tipo in ("gastos", "ingresos"):
            movimiento = services.guardar_movimiento(tipo, 1, self.datos_movimiento(tipo))
            self.assertIsInstance(movimiento["monto"], Decimal)
            self.assertIsInstance(movimiento["fecha"], date)
            self.assertEqual(services.obtener_movimiento(tipo, 1, movimiento["id"]), movimiento)
            antes = self.estado(tipo)
            with self.assertRaises(MovimientoNoEncontrado):
                services.obtener_movimiento(tipo, 2, movimiento["id"])
            with self.assertRaises(MovimientoNoEncontrado):
                services.guardar_movimiento(tipo, 2, self.datos_movimiento(tipo), movimiento["id"])
            with self.assertRaises(MovimientoNoEncontrado):
                services.eliminar_movimiento(tipo, 2, movimiento["id"])
            self.assertEqual(self.estado(tipo), antes)

    def test_formulario_de_alta_invalido_no_se_interpreta_como_consulta(self):
        services.guardar_movimiento("gastos", 1, self.datos_movimiento())
        response = self.client.post("/gastos", self.datos_movimiento(monto="-1", categoria="Nueva"))
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(response.context["categoria_form"].is_bound)
        self.assertFalse(response.context["filtrado"])
        self.assertEqual(response.context["total"], Decimal("25.50"))

    def test_ambos_filtros_invalidos_muestran_ambos_errores(self):
        response = self.client.get("/gastos", {"mes": "13", "anio": "2026", "categoria": "No existe"})
        self.assertTrue(response.context["periodo_form"].errors)
        self.assertTrue(response.context["categoria_form"].errors)
        self.assertIsNone(response.context["total"])
        self.assertEqual(response.context["movimientos"], [])

    def test_tarjetas_conservan_clasificacion_y_enlaces_de_cada_tipo(self):
        for tipo, etiqueta, valor in (("gastos", "Categoría", "Comida"), ("ingresos", "Origen", "Trabajo")):
            movimiento = services.guardar_movimiento(tipo, 1, self.datos_movimiento(tipo))
            response = self.client.get(f"/{tipo}")
            self.assertContains(response, f"<strong>{etiqueta}:</strong> {valor}", html=False)
            self.assertContains(response, f'href="/{tipo}/editar/{movimiento["id"]}"')
            self.assertContains(response, f'action="/{tipo}/eliminar/{movimiento["id"]}"')

    def test_crud_completo_de_ambos_tipos(self):
        for tipo in ("gastos", "ingresos"):
            with self.subTest(tipo=tipo):
                self.assertEqual(self.client.post(f"/{tipo}", self.datos_movimiento(tipo)).status_code, 302)
                fila = services.listar_movimientos(tipo, 1)[0]
                self.assertEqual(fila["monto"], Decimal("25.50"))
                response = self.client.get(f"/{tipo}/editar/{fila['id']}")
                self.assertContains(response, 'value="2026-10-17"')
                self.assertEqual(self.client.post(f"/{tipo}/editar/{fila['id']}",
                                                 self.datos_movimiento(tipo, monto="30.05")).status_code, 302)
                self.assertEqual(services.sumar_montos(services.listar_movimientos(tipo, 1)), Decimal("30.05"))
                self.assertEqual(self.client.get(f"/{tipo}/eliminar/{fila['id']}").status_code, 405)
                self.assertEqual(self.client.post(f"/{tipo}/eliminar/{fila['id']}").status_code, 302)
                self.assertEqual(services.listar_movimientos(tipo, 1), [])

    def test_balance_exactitud_y_periodos(self):
        self.assertEqual(services.calcular_balance(1)["balance"], Decimal("0.00"))
        services.guardar_movimiento("ingresos", 1, self.datos_movimiento("ingresos", monto="100.00"))
        services.guardar_movimiento("gastos", 1, self.datos_movimiento())
        services.guardar_movimiento("gastos", 2, self.datos_movimiento(monto="999"))
        self.assertEqual(services.calcular_balance(1)["balance"], Decimal("74.50"))
        self.assertEqual(services.calcular_balance(1, mes=10, anio=2026)["balance"], Decimal("74.50"))
        self.assertEqual(services.calcular_balance(1, mes=10, anio=2025)["balance"], Decimal("0.00"))
        services.guardar_movimiento("gastos", 1, self.datos_movimiento(monto="0.10"))
        services.guardar_movimiento("gastos", 1, self.datos_movimiento(monto="0.20"))
        self.assertEqual(services.calcular_balance(1)["total_gastos"], Decimal("25.80"))
        response = self.client.post("/balance/mensual", {"mes": 10, "anio": 2026})
        self.assertEqual(response.context["resumen_mes"]["balance"], Decimal("74.20"))

    def test_montos_invalidos_no_escriben_y_preservan_formulario(self):
        for tipo in ("gastos", "ingresos"):
            for monto in ("0", "-1", "NaN", "Infinity", "0.001", "texto", "1000000000000.00"):
                with self.subTest(tipo=tipo, monto=monto):
                    antes = self.estado(tipo)
                    response = self.client.post(f"/{tipo}", self.datos_movimiento(tipo, monto=monto))
                    self.assertEqual(response.status_code, 200)
                    self.assertIn("monto", response.context["form"].errors)
                    self.assertEqual(response.context["form"]["descripcion"].value(), "Prueba")
                    self.assertEqual(self.estado(tipo), antes)

    def test_fechas_y_campos_invalidos_no_escriben(self):
        for cambios in ({"fecha": "invalida"}, {"fecha": "2025-02-29"},
                        {"categoria": "   "}, {"descripcion": ""}):
            response = self.client.post("/gastos", self.datos_movimiento(**cambios))
            self.assertTrue(response.context["form"].errors)
            self.assertEqual(services.listar_movimientos("gastos", 1), [])
        self.assertEqual(self.client.post("/gastos", self.datos_movimiento(fecha="2024-02-29")).status_code, 302)

    def test_servicios_validan_sin_depender_de_vistas(self):
        with self.assertRaises(ValidationError):
            services.guardar_movimiento("gastos", 1, self.datos_movimiento(monto="NaN"))
        with self.assertRaises(ValidationError):
            services.listar_movimientos("gastos", 1, mes=13, anio=2026)

    def test_aislamiento_por_usuario_en_listados_edicion_y_borrado(self):
        for tipo in ("gastos", "ingresos"):
            fila = services.guardar_movimiento(tipo, 2, self.datos_movimiento(tipo, descripcion="Privado de B"))
            antes = self.estado(tipo)
            self.assertNotContains(self.client.get(f"/{tipo}"), "Privado de B")
            self.assertEqual(self.client.get(f"/{tipo}/editar/{fila['id']}").status_code, 404)
            self.assertEqual(self.client.post(f"/{tipo}/editar/{fila['id']}", self.datos_movimiento(tipo)).status_code, 404)
            self.assertEqual(self.client.post(f"/{tipo}/eliminar/{fila['id']}").status_code, 404)
            self.assertEqual(self.estado(tipo), antes)

    def test_propietario_del_formulario_se_ignora(self):
        self.client.post("/gastos", self.datos_movimiento(user_id=2))
        self.assertEqual(len(services.listar_movimientos("gastos", 1)), 1)
        self.assertEqual(services.listar_movimientos("gastos", 2), [])

    def test_edicion_invalida_conserva_original(self):
        fila = services.guardar_movimiento("gastos", 1, self.datos_movimiento())
        antes = self.estado("gastos")
        response = self.client.post(f"/gastos/editar/{fila['id']}", self.datos_movimiento(monto="-4", descripcion="Intento"))
        self.assertContains(response, "Intento")
        self.assertEqual(self.estado("gastos"), antes)

    def test_filtros_combinados_listado_y_total_coinciden(self):
        services.guardar_movimiento("gastos", 1, self.datos_movimiento())
        services.guardar_movimiento("gastos", 1, self.datos_movimiento(monto="5", categoria="Transporte"))
        services.guardar_movimiento("gastos", 1, self.datos_movimiento(monto="10", fecha="2026-09-30"))
        response = self.client.get("/gastos", {"mes": 10, "anio": 2026, "categoria": "Comida"})
        self.assertEqual(len(response.context["movimientos"]), 1)
        self.assertEqual(response.context["total"], Decimal("25.50"))
        mensual = self.client.post("/gastos/mensuales", {"mes": 10, "anio": 2026})
        self.assertEqual(mensual.context["total"], Decimal("30.50"))
        categoria = self.client.post("/gastos/categoria", {"categoria": "Comida"})
        self.assertEqual(categoria.context["total"], Decimal("35.50"))

    def test_categoria_no_perteneciente_se_rechaza(self):
        services.guardar_movimiento("gastos", 2, self.datos_movimiento(categoria="SoloB"))
        response = self.client.get("/gastos", {"categoria": "SoloB"})
        self.assertTrue(response.context["categoria_form"].errors)
        self.assertIsNone(response.context["total"])

    def test_mes_invalido_muestra_error_y_no_total_enganoso(self):
        for mes in ("0", "13", "x"):
            response = self.client.post("/gastos/mensuales", {"mes": mes, "anio": 2026})
            self.assertTrue(response.context["periodo_form"].errors)
            self.assertIsNone(response.context["total"])
            response = self.client.get("/balance", {"mes": mes, "anio": 2026})
            self.assertTrue(response.context["form"].errors)
            self.assertIsNone(response.context["resumen_mes"])

    def test_csrf_todas_las_mutaciones(self):
        cliente = Client(enforce_csrf_checks=True)
        cliente.get("/iniciarSesion")
        cliente.post("/iniciarSesion", {"email": "uno@example.test", "password": self.password,
                                        "csrfmiddlewaretoken": cliente.cookies["csrftoken"].value})
        for tipo in ("gastos", "ingresos"):
            fila = services.guardar_movimiento(tipo, 1, self.datos_movimiento(tipo))
            for url in (f"/{tipo}", f"/{tipo}/editar/{fila['id']}", f"/{tipo}/eliminar/{fila['id']}"):
                self.assertEqual(cliente.post(url, self.datos_movimiento(tipo)).status_code, 403)
            token = cliente.cookies["csrftoken"].value
            self.assertEqual(cliente.post(f"/{tipo}", self.datos_movimiento(tipo, csrfmiddlewaretoken=token)).status_code, 302)

    def test_plantillas_no_son_archivos_publicos(self):
        for url in ("/Front%20End/funcionalidades/gastos.html", "/templates/finanzas/movimientos.html", "/Datos/usuarios.json"):
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_plantillas_tienen_viewport_y_campos_fecha(self):
        for url in ("/panel", "/gastos", "/ingresos", "/balance"):
            self.assertContains(self.client.get(url), 'name="viewport"')

    def test_ingresos_mensuales_y_orden(self):
        services.guardar_movimiento("ingresos", 1, self.datos_movimiento("ingresos", fecha="2026-01-01"))
        services.guardar_movimiento("ingresos", 1, self.datos_movimiento("ingresos", fecha="2025-12-31"))
        response = self.client.post("/ingresos/mensuales", {"mes": 1, "anio": 2026})
        self.assertEqual(len(response.context["movimientos"]), 1)
        self.assertEqual(response.context["total"], Decimal("25.50"))
        self.assertEqual(services.listar_movimientos("ingresos", 1)[0]["fecha"].isoformat(), "2026-01-01")
