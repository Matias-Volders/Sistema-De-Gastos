from datetime import datetime
import persistencia

def calcularBalance():
    total_gastos = sum(gasto["monto"] for gasto in persistencia.gastos)
    total_ingresos = sum(ingreso["monto"] for ingreso in persistencia.ingresos)
    balance = total_ingresos - total_gastos

    print("Total de gastos:", total_gastos)
    print("Total de ingresos:", total_ingresos)
    print("Balance total:", balance)

def balanceMensual():
    try:
        mes = int(input("Ingrese el mes (1-12): "))
        anio = int(input("Ingrese el año: "))
    except ValueError:
        print("Debe ingresar números válidos.")
        return

    total_gastos = 0
    total_ingresos = 0

    for gasto in persistencia.gastos:
        fecha = datetime.strptime(gasto["fecha"], "%d/%m/%Y %H:%M:%S")
        if fecha.month == mes and fecha.year == anio:
            total_gastos += gasto["monto"]

    for ingreso in persistencia.ingresos:
        fecha = datetime.strptime(ingreso["fecha"], "%d/%m/%Y %H:%M:%S")
        if fecha.month == mes and fecha.year == anio:
            total_ingresos += ingreso["monto"]

    balance = total_ingresos - total_gastos

    print(f"\n--- BALANCE DE {mes:02d}/{anio} ---")
    print(f"Total ingresos: ${total_ingresos}")
    print(f"Total gastos: ${total_gastos}")
    print(f"Balance: ${balance}")

def calcular_balance_total_web():
    total_gastos = sum(gasto["monto"] for gasto in persistencia.gastos)
    total_ingresos = sum(ingreso["monto"] for ingreso in persistencia.ingresos)

    return {
        "total_gastos": total_gastos,
        "total_ingresos": total_ingresos,
        "balance": total_ingresos - total_gastos
    }

def balance_mensual_web(mes, anio):
    total_gastos = 0
    total_ingresos = 0

    for gasto in persistencia.gastos:
        fecha = datetime.strptime(gasto["fecha"], "%d/%m/%Y %H:%M:%S")
        if fecha.month == int(mes) and fecha.year == int(anio):
            total_gastos += gasto["monto"]

    for ingreso in persistencia.ingresos:
        fecha = datetime.strptime(ingreso["fecha"], "%d/%m/%Y %H:%M:%S")
        if fecha.month == int(mes) and fecha.year == int(anio):
            total_ingresos += ingreso["monto"]

    return {
        "ingresos": total_ingresos,
        "gastos": total_gastos,
        "balance": total_ingresos - total_gastos
    }