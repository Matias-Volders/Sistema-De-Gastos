"""Entrada HTTP: permisos, formularios, llamadas a servicios y respuestas."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from backend.finanzas import services
from backend.finanzas.configuracion import obtener_configuracion
from backend.finanzas.exceptions import MovimientoNoEncontrado
from backend.finanzas.forms import PeriodoForm
from backend.finanzas.presentacion import preparar_listado


@login_required
@require_http_methods(["GET", "POST"])
def movimientos(request, tipo, consulta=None):
    configuracion = obtener_configuracion(tipo)
    es_alta = request.method == "POST" and consulta is None
    form = configuracion.formulario(request.POST if es_alta else None)
    if es_alta and form.is_valid():
        services.guardar_movimiento(tipo, request.user.pk, form.cleaned_data)
        messages.success(request, "Movimiento registrado correctamente.")
        return redirect(tipo)

    # Un alta inválida conserva sus errores, sin interpretar sus campos como filtros.
    datos_consulta = {} if es_alta else (request.POST if request.method == "POST" else request.GET)
    contexto = preparar_listado(tipo, request.user.pk, datos_consulta, consulta)
    return render(request, "finanzas/movimientos.html", {**contexto, "form": form})


@login_required
@require_http_methods(["GET", "POST"])
def editar(request, tipo, movimiento_id):
    configuracion = obtener_configuracion(tipo)
    try:
        movimiento = services.obtener_movimiento(tipo, request.user.pk, movimiento_id)
        form = configuracion.formulario(
            request.POST if request.method == "POST" else None, initial=movimiento
        )
        if request.method == "POST" and form.is_valid():
            services.guardar_movimiento(tipo, request.user.pk, form.cleaned_data, movimiento_id)
            messages.success(request, "Movimiento editado correctamente.")
            return redirect(tipo)
    except MovimientoNoEncontrado as exc:
        raise Http404(str(exc)) from exc
    return render(request, "finanzas/editar.html", {
        "tipo": tipo, "configuracion": configuracion, "form": form,
    })


@login_required
@require_POST
def eliminar(request, tipo, movimiento_id):
    try:
        services.eliminar_movimiento(tipo, request.user.pk, movimiento_id)
    except MovimientoNoEncontrado as exc:
        raise Http404(str(exc)) from exc
    messages.success(request, "Movimiento eliminado correctamente.")
    return redirect(tipo)


@login_required
@require_http_methods(["GET", "POST"])
def balance(request):
    datos = request.POST if request.method == "POST" else request.GET
    consultar = request.method == "POST" or "mes" in datos or "anio" in datos
    form = PeriodoForm(datos if consultar else None)
    resumen_mes = None
    if consultar and form.is_valid():
        resumen_mes = services.calcular_balance(request.user.pk, **form.cleaned_data)
    return render(request, "finanzas/balance.html", {
        "resumen": services.calcular_balance(request.user.pk), "form": form, "resumen_mes": resumen_mes,
    })
