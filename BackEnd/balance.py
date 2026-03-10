from datetime import datetime
import persistencia
import gastos
import ingresos

def calcular_balance(user_id):
    total_ingresos = ingresos.total_ingresos_usuario(user_id)
    total_gastos = gastos.total_gastos_usuario(user_id)

    return {
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance": total_ingresos - total_gastos
    }


def total_ingresos_mensuales(user_id, mes, anio):
    ingresos_usuario = ingresos.obtener_ingresos_usuario(user_id)
    total = 0

    for ingreso in ingresos_usuario:
        fecha_obj = datetime.strptime(ingreso["fecha"], "%Y-%m-%d")
        if fecha_obj.month == int(mes) and fecha_obj.year == int(anio):
            total += ingreso["monto"]

    return total


def calcular_balance_mensual(user_id, mes, anio):
    total_ingresos_mes = total_ingresos_mensuales(user_id, mes, anio)
    total_gastos_mes = gastos.total_gastos_mensuales(user_id, mes, anio)

    return {
        "total_ingresos_mes": total_ingresos_mes,
        "total_gastos_mes": total_gastos_mes,
        "balance_mes": total_ingresos_mes - total_gastos_mes
    }