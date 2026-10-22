"""Casos de uso: validaciones compartidas y cálculos sobre consultas SQL."""
from decimal import Decimal
from django.core.exceptions import ValidationError

from backend.finanzas import repository
from backend.finanzas.configuracion import obtener_configuracion
from backend.finanzas.forms import PeriodoForm


def validar_periodo(mes=None, anio=None):
    if mes is None and anio is None:
        return {}
    formulario = PeriodoForm({"mes": mes, "anio": anio})
    if not formulario.is_valid():
        raise ValidationError(formulario.errors.as_data())
    return formulario.cleaned_data


def listar_movimientos(tipo, user_id, *, mes=None, anio=None, categoria=None):
    return repository.listar_del_usuario(
        tipo, user_id, categoria=categoria, **validar_periodo(mes, anio)
    )


def obtener_movimiento(tipo, user_id, movimiento_id):
    return repository.obtener_del_usuario(tipo, user_id, movimiento_id)


def guardar_movimiento(tipo, user_id, datos, movimiento_id=None):
    if type(user_id) is not int or user_id < 1:
        raise ValidationError("Usuario inválido.")
    formulario = obtener_configuracion(tipo).formulario(datos)
    if not formulario.is_valid():
        raise ValidationError(formulario.errors.as_data())
    return repository.guardar_del_usuario(tipo, user_id, formulario.cleaned_data, movimiento_id)


def eliminar_movimiento(tipo, user_id, movimiento_id):
    repository.eliminar_del_usuario(tipo, user_id, movimiento_id)


def listar_categorias(user_id):
    return repository.listar_categorias(user_id)


def sumar_montos(movimientos):
    """Utilidad para conjuntos ya cargados; los resúmenes de pantalla usan SQL."""
    return sum((movimiento["monto"] for movimiento in movimientos), Decimal("0.00"))


def total_movimientos(tipo, user_id, *, mes=None, anio=None, categoria=None):
    return repository.sumar_del_usuario(tipo, user_id, categoria=categoria, **validar_periodo(mes, anio))


def calcular_balance(user_id, mes=None, anio=None):
    resumen = repository.resumen_del_usuario(user_id, **validar_periodo(mes, anio))
    return {**resumen, "balance": resumen["total_ingresos"] - resumen["total_gastos"]}
