"""Prepara formularios de consulta y datos para la plantilla de movimientos."""
from backend.finanzas import services
from backend.finanzas.configuracion import obtener_configuracion
from backend.finanzas.forms import CategoriaForm, PeriodoForm


def preparar_listado(tipo, user_id, datos, consulta=None):
    configuracion = obtener_configuracion(tipo)
    filtrar_mes = consulta == "mes" or "mes" in datos or "anio" in datos
    filtrar_categoria = configuracion.permite_categoria and (
        consulta == "categoria" or bool(datos.get("categoria"))
    )
    categorias = services.listar_categorias(user_id) if configuracion.permite_categoria else []
    periodo_form = PeriodoForm(datos if filtrar_mes else None)
    categoria_form = CategoriaForm(
        datos if filtrar_categoria else None, categorias=categorias, auto_id="filtro_%s"
    )

    filtros = {}
    filtros_validos = True
    for activo, formulario in ((filtrar_mes, periodo_form), (filtrar_categoria, categoria_form)):
        if activo:
            if formulario.is_valid():
                filtros.update(formulario.cleaned_data)
            else:
                filtros_validos = False

    movimientos = services.listar_movimientos(tipo, user_id, **filtros) if filtros_validos else []
    # La etiqueta de cada tarjeta es presentación; no se persiste.
    tarjetas = [
        {**movimiento, "clasificacion": movimiento[configuracion.campo_clasificacion]}
        for movimiento in movimientos
    ]
    return {
        "tipo": tipo,
        "titulo": tipo.capitalize(),
        "configuracion": configuracion,
        "periodo_form": periodo_form,
        "categoria_form": categoria_form,
        "movimientos": tarjetas,
        "filtrado": filtrar_mes or filtrar_categoria,
        "total": services.total_movimientos(tipo, user_id, **filtros) if filtros_validos else None,
    }
