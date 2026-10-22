from django.urls import path
from backend.finanzas import views

urlpatterns = [
    path("gastos", views.movimientos, {"tipo": "gastos"}, name="gastos"),
    path("gastos/mensuales", views.movimientos, {"tipo": "gastos", "consulta": "mes"}, name="gastos_mensuales"),
    path("gastos/categoria", views.movimientos, {"tipo": "gastos", "consulta": "categoria"}, name="gastos_categoria"),
    path("gastos/editar/<int:movimiento_id>", views.editar, {"tipo": "gastos"}, name="editar_gasto"),
    path("gastos/eliminar/<int:movimiento_id>", views.eliminar, {"tipo": "gastos"}, name="eliminar_gasto"),
    path("ingresos", views.movimientos, {"tipo": "ingresos"}, name="ingresos"),
    path("ingresos/mensuales", views.movimientos, {"tipo": "ingresos", "consulta": "mes"}, name="ingresos_mensuales"),
    path("ingresos/editar/<int:movimiento_id>", views.editar, {"tipo": "ingresos"}, name="editar_ingreso"),
    path("ingresos/eliminar/<int:movimiento_id>", views.eliminar, {"tipo": "ingresos"}, name="eliminar_ingreso"),
    path("balance", views.balance, name="balance"),
    path("balance/mensual", views.balance, name="balance_mensual"),
]
