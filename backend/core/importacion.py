"""Importación explícita, idempotente para copias idénticas y transaccional."""
from collections import defaultdict
from decimal import Decimal

from django.core.management.color import no_style
from django.db import connection, transaction
from django.db.models import Count, Sum

from backend.core.legacy import ErrorImportacion
from backend.finanzas.models import Categoria, Egreso, Ingreso
from backend.finanzas.repository import obtener_o_crear_categoria
from backend.usuarios.models import Usuario


def _coincide_registro(actual, fila, *, egreso=False):
    campos = ("usuario_id", "monto", "fecha", "descripcion")
    if any(getattr(actual, campo) != fila[campo] for campo in campos):
        return False
    if egreso:
        return actual.categoria.nombre.strip().lower() == fila["categoria"].strip().lower()
    return actual.origen == fila["origen"]


def validar_destino(datos):
    nuevas = {"usuarios": 0, "ingresos": 0, "egresos": 0}
    for posicion, fila in enumerate(datos.usuarios, start=1):
        actual = Usuario.objects.filter(pk=fila["id"]).first()
        correo_ocupado = Usuario.objects.filter(email__iexact=fila["email"]).exclude(pk=fila["id"]).exists()
        if correo_ocupado or (actual and any(getattr(actual, campo) != fila[campo]
                                            for campo in ("nombre", "email", "password"))):
            raise ErrorImportacion(f"Conflicto en usuarios, fila {posicion}. No se sobrescriben cuentas existentes.")
        nuevas["usuarios"] += actual is None
    for nombre, modelo, filas in (("ingresos", Ingreso, datos.ingresos), ("egresos", Egreso, datos.gastos)):
        for posicion, fila in enumerate(filas, start=1):
            consulta = modelo.objects.filter(pk=fila["id"])
            if modelo is Egreso:
                consulta = consulta.select_related("categoria")
            actual = consulta.first()
            if actual and not _coincide_registro(actual, fila, egreso=modelo is Egreso):
                raise ErrorImportacion(f"Conflicto en {nombre}, fila {posicion}. No se sobrescriben registros.")
            nuevas[nombre] += actual is None
    return nuevas


def _conciliar(filas, modelo):
    esperado = defaultdict(lambda: {"cantidad": 0, "total": Decimal("0.00")})
    for fila in filas:
        clave = (fila["usuario_id"], fila["fecha"].year, fila["fecha"].month)
        esperado[clave]["cantidad"] += 1
        esperado[clave]["total"] += fila["monto"]
    consulta = modelo.objects.filter(pk__in=[fila["id"] for fila in filas]).order_by().values(
        "usuario_id", "fecha__year", "fecha__month"
    ).annotate(cantidad=Count("id"), total=Sum("monto"))
    obtenido = {
        (fila["usuario_id"], fila["fecha__year"], fila["fecha__month"]):
            {"cantidad": fila["cantidad"], "total": fila["total"]}
        for fila in consulta
    }
    if dict(esperado) != obtenido:
        raise ErrorImportacion("La conciliación por usuario y período no coincide; se revierte la importación.")


def ejecutar_importacion(datos, *, aplicar=False, respaldo_en=None):
    with transaction.atomic():
        if aplicar:
            # Orden fijo y bloqueo durante la carga: evita carreras con otra importación
            # o escrituras de la aplicación mientras se conservan IDs anteriores.
            with connection.cursor() as cursor:
                cursor.execute("LOCK TABLE usuario, categoria, ingreso, egreso IN SHARE ROW EXCLUSIVE MODE")
        nuevas = validar_destino(datos)
        if not aplicar:
            return {"nuevas": nuevas, "respaldo": None, "aplicado": False}

        respaldo = datos.respaldar(respaldo_en)
        for fila in datos.usuarios:
            if not Usuario.objects.filter(pk=fila["id"]).exists():
                Usuario.objects.create(**fila)
        for fila in datos.ingresos:
            if not Ingreso.objects.filter(pk=fila["id"]).exists():
                Ingreso.objects.create(**fila)
        for fila in datos.gastos:
            if not Egreso.objects.filter(pk=fila["id"]).exists():
                campos = {clave: valor for clave, valor in fila.items() if clave != "categoria"}
                categoria = obtener_o_crear_categoria(fila["usuario_id"], fila["categoria"])
                Egreso.objects.create(**campos, categoria=categoria)

        _conciliar(datos.ingresos, Ingreso)
        _conciliar(datos.gastos, Egreso)
        # IDs explícitos de JSON: alinear secuencias para futuras altas automáticas.
        with connection.cursor() as cursor:
            for sentencia in connection.ops.sequence_reset_sql(no_style(), [Usuario, Categoria, Ingreso, Egreso]):
                cursor.execute(sentencia)
        return {"nuevas": nuevas, "respaldo": respaldo, "aplicado": True}
