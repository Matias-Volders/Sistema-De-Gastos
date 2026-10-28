"""Consultas ORM sobre Ingreso y Egreso. Los filtros y las sumas corren en SQL."""
from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import DecimalField, OuterRef, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Lower, Trim

from backend.finanzas.exceptions import MovimientoNoEncontrado
from backend.finanzas.models import Categoria, Egreso, Ingreso
from backend.usuarios.models import Usuario

MODELOS = {"gastos": Egreso, "ingresos": Ingreso}


def obtener_modelo(tipo):
    try:
        return MODELOS[tipo]
    except KeyError as exc:
        raise ValueError("Tipo de registro financiero inválido.") from exc


def consultar_del_usuario(tipo, user_id, *, mes=None, anio=None, categoria=None):
    consulta = obtener_modelo(tipo).objects.filter(usuario_id=user_id)
    if mes is not None:
        # Rango sobre la fecha: permite aprovechar el índice compuesto.
        inicio = date(anio, mes, 1)
        fin = date(anio, mes, monthrange(anio, mes)[1])
        consulta = consulta.filter(fecha__gte=inicio, fecha__lte=fin)
    if categoria:
        if tipo != "gastos":
            return consulta.none()
        consulta = consulta.alias(nombre_categoria=Lower(Trim("categoria__nombre"))).filter(
            nombre_categoria=categoria.strip().lower()
        )
    return consulta


def como_datos(registro):
    datos = {
        "id": registro.pk, "user_id": registro.usuario_id,
        "monto": registro.monto, "fecha": registro.fecha, "descripcion": registro.descripcion,
    }
    if isinstance(registro, Egreso):
        datos["categoria"] = registro.categoria.nombre
    else:
        datos["origen"] = registro.origen
    return datos


def listar_del_usuario(tipo, user_id, **filtros):
    consulta = consultar_del_usuario(tipo, user_id, **filtros)
    if tipo == "gastos":
        consulta = consulta.select_related("categoria")
    return [como_datos(registro) for registro in consulta]


def _obtener(consulta, movimiento_id):
    try:
        return consulta.get(pk=movimiento_id)
    except consulta.model.DoesNotExist as exc:
        raise MovimientoNoEncontrado("No se encontró el registro.") from exc


def obtener_del_usuario(tipo, user_id, movimiento_id):
    consulta = consultar_del_usuario(tipo, user_id)
    if tipo == "gastos":
        consulta = consulta.select_related("categoria")
    return como_datos(_obtener(consulta, movimiento_id))


def obtener_o_crear_categoria(user_id, nombre):
    nombre = nombre.strip()
    # La restricción UNIQUE resuelve también altas simultáneas del mismo nombre.
    categoria, _ = Categoria.objects.alias(clave=Lower(Trim("nombre"))).get_or_create(
        usuario_id=user_id, clave__exact=nombre.lower(), defaults={"nombre": nombre}
    )
    return categoria


@transaction.atomic
def guardar_del_usuario(tipo, user_id, datos_validados, movimiento_id=None):
    modelo = obtener_modelo(tipo)
    if movimiento_id is None:
        registro = modelo(usuario_id=user_id)
    else:
        registro = _obtener(modelo.objects.select_for_update().filter(usuario_id=user_id), movimiento_id)
    for campo in ("monto", "fecha", "descripcion"):
        setattr(registro, campo, datos_validados[campo])
    if modelo is Egreso:
        registro.categoria = obtener_o_crear_categoria(user_id, datos_validados["categoria"])
    else:
        registro.origen = datos_validados["origen"]
    registro.save()
    return como_datos(registro)


@transaction.atomic
def eliminar_del_usuario(tipo, user_id, movimiento_id):
    consulta = obtener_modelo(tipo).objects.select_for_update().filter(usuario_id=user_id)
    _obtener(consulta, movimiento_id).delete()


def listar_categorias(user_id):
    return list(Categoria.objects.filter(usuario_id=user_id).order_by(Lower("nombre"), "pk").values_list("nombre", flat=True))


def sumar_del_usuario(tipo, user_id, **filtros):
    return consultar_del_usuario(tipo, user_id, **filtros).aggregate(total=Sum("monto", default=Decimal("0.00")))["total"]


def resumen_del_usuario(user_id, **periodo):
    def suma_correlacionada(tipo):
        return consultar_del_usuario(tipo, OuterRef("pk"), **periodo).order_by().values(
            "usuario_id"
        ).annotate(total=Sum("monto")).values("total")

    dinero = DecimalField(max_digits=24, decimal_places=2)
    resumen = Usuario.objects.filter(pk=user_id).annotate(
        total_ingresos=Coalesce(Subquery(suma_correlacionada("ingresos")), Value(Decimal("0.00")), output_field=dinero),
        total_gastos=Coalesce(Subquery(suma_correlacionada("gastos")), Value(Decimal("0.00")), output_field=dinero),
    ).values("total_ingresos", "total_gastos").first()
    # Una sola sentencia SQL calcula ambos totales sobre la misma instantánea.
    return resumen or {"total_ingresos": Decimal("0.00"), "total_gastos": Decimal("0.00")}
