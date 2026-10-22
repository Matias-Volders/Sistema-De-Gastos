"""Diferencias declaradas entre las pantallas que comparten el mismo flujo."""
from dataclasses import dataclass

from backend.finanzas.forms import GastoForm, IngresoForm


@dataclass(frozen=True)
class ConfiguracionMovimiento:
    formulario: type
    singular: str
    campo_clasificacion: str
    etiqueta_clasificacion: str
    url_editar: str
    url_eliminar: str
    permite_categoria: bool = False


TIPOS_MOVIMIENTO = {
    "gastos": ConfiguracionMovimiento(
        formulario=GastoForm,
        singular="gasto",
        campo_clasificacion="categoria",
        etiqueta_clasificacion="Categoría",
        url_editar="editar_gasto",
        url_eliminar="eliminar_gasto",
        permite_categoria=True,
    ),
    "ingresos": ConfiguracionMovimiento(
        formulario=IngresoForm,
        singular="ingreso",
        campo_clasificacion="origen",
        etiqueta_clasificacion="Origen",
        url_editar="editar_ingreso",
        url_eliminar="eliminar_ingreso",
    ),
}


def obtener_configuracion(tipo):
    try:
        return TIPOS_MOVIMIENTO[tipo]
    except KeyError as exc:
        raise ValueError("Tipo de movimiento inválido.") from exc
