from datetime import datetime

gastos = []
ingresos = []

def registrarGastos():
    print("Registrar Gastos")
    monto = float(input("Ingrese el monto del gasto: "))
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    categoria = input("Ingrese la categoría del gasto: ")
    descripcion = input("Ingrese una descripción del gasto: ")
    gasto = {
        "monto": monto,
        "fecha": fecha,
        "categoria": categoria,
        "descripcion": descripcion
        }
    gastos.append(gasto)
    print("Gasto registrado exitosamente.")

def registrarIngresos():
    print("Registrar Ingresos")
    monto = float(input("Ingrese el monto del ingreso: "))
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    origen = input("Ingrese el origen del ingreso: ")
    descripcion = input("Ingrese una descripción del ingreso: ")
    ingreso = {
        "monto": monto,
        "fecha": fecha,
        "origen": origen,
        "descripcion": descripcion
        } #asi se crea un diccionario con los datos del ingreso
    ingresos.append(ingreso)
    print("Ingreso registrado exitosamente.")

def calcularBalance():
    print("Calcular Balance")
    total_gastos = sum(gasto["monto"] for gasto in gastos)#calcula la suma de los montos de los gastos
    total_ingresos = sum(ingreso["monto"] for ingreso in ingresos)#calcula la suma de los montos de los ingresos
    balance = total_ingresos - total_gastos

    print("Total de gastos:", total_gastos)
    print("Total de ingresos:", total_ingresos)
    print("Balance total:", balance)

def mostrarGastos():
    if not gastos:
        print("No hay gastos registrados.")
        return
    print("Gastos Registrados:")
    for gasto in gastos:
        print(f"\n Monto: {gasto['monto']}, Fecha: {gasto['fecha']}, Categoría: {gasto['categoria']}, Descripción: {gasto['descripcion']}")

def mostrarIngresos():
    if not ingresos:
        print("No hay ingresos registrados.")
        return
    print("Ingresos Registrados:")
    for ingreso in ingresos:
        print(f"\n Monto: {ingreso['monto']}, Origen: {ingreso['origen']}, Descripción: {ingreso['descripcion']}")

def gastosPorCategoria():
    categorias = {}
    for gasto in gastos:
        categoria = gasto["categoria"]
        monto = gasto["monto"]
        if categoria in categorias:
            categorias[categoria] += monto
        else:
            categorias[categoria] = monto
    print("Gastos por Categoría:")
    for categoria, monto in categorias.items():
        print(f"{categoria}: {monto}")

def gastosMensuales():
    meses = {}
    for gasto in gastos:
        fecha = datetime.strptime(gasto["fecha"], "%d/%m/%Y %H:%M:%S")
        mes = fecha.strftime("%Y-%m")
        monto = gasto["monto"]
        if mes in meses:
            meses[mes] += monto
        else:
            meses[mes] = monto
    print("Gastos Mensuales:")
    for mes, monto in meses.items():
        print(f"{mes}: {monto}")
    sumaDeGastos = sum(meses.values())
    print("\n Resumen Mensual:", sumaDeGastos)