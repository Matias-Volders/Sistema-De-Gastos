import json
import os
from datetime import datetime

gastos = []
ingresos = []

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_DIR = os.path.join(BASE_DIR, "Datos")

RUTA_GASTOS = os.path.join(DATOS_DIR, "gastos.json")
RUTA_INGRESOS = os.path.join(DATOS_DIR, "ingresos.json")

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
    guardar_gastos()
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
    guardar_ingresos()
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
        print(f"\n Monto: {ingreso['monto']}, Fecha: {ingreso['fecha']}, Origen: {ingreso['origen']}, Descripción: {ingreso['descripcion']}")

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
    mes_actual = datetime.now().strftime("%Y-%m")
    total_mes = 0

    for gasto in gastos:
        fecha = datetime.strptime(gasto["fecha"], "%d/%m/%Y %H:%M:%S")
        mes_gasto = fecha.strftime("%Y-%m")

        if mes_gasto == mes_actual:
            total_mes += gasto["monto"]

    print(f"Gastos del mes actual ({mes_actual}): {total_mes}")

def editarGasto():
    if not gastos:
        print("No hay gastos registrados para editar.")
        return

    print("Gastos registrados:")
    for i, gasto in enumerate(gastos, start=1):
        print(f"\n[{i}] Monto: {gasto['monto']}, Fecha: {gasto['fecha']}, Categoría: {gasto['categoria']}, Descripción: {gasto['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del gasto que quiere editar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(gastos):
        print("Número inválido.")
        return

    gasto = gastos[opcion - 1]

    print("\nDeje vacío y presione Enter si quiere mantener el valor actual.")

    nuevo_monto = input(f"Nuevo monto [{gasto['monto']}]: ").strip()
    if nuevo_monto != "":
        try:
            nuevo_monto = float(nuevo_monto)
            if nuevo_monto <= 0:
                print("El monto debe ser mayor a 0.")
                return
            gasto["monto"] = nuevo_monto
        except ValueError:
            print("El monto debe ser un número válido.")
            return

    nueva_categoria = input(f"Nueva categoría [{gasto['categoria']}]: ").strip()
    if nueva_categoria != "":
        gasto["categoria"] = nueva_categoria

    nueva_descripcion = input(f"Nueva descripción [{gasto['descripcion']}]: ").strip()
    if nueva_descripcion != "":
        gasto["descripcion"] = nueva_descripcion

    guardar_gastos()
    print("Gasto editado exitosamente.")

def editarIngreso():
    if not ingresos:
        print("No hay ingresos registrados para editar.")
        return

    print("Ingresos registrados:")
    for i, ingreso in enumerate(ingresos, start=1):
        print(f"\n[{i}] Monto: {ingreso['monto']}, Fecha: {ingreso['fecha']}, Origen: {ingreso['origen']}, Descripción: {ingreso['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del ingreso que quiere editar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(ingresos):
        print("Número inválido.")
        return

    ingreso = ingresos[opcion - 1]

    print("\nDeje vacío y presione Enter si quiere mantener el valor actual.")

    nuevo_monto = input(f"Nuevo monto [{ingreso['monto']}]: ").strip()
    if nuevo_monto != "":
        try:
            nuevo_monto = float(nuevo_monto)
            if nuevo_monto <= 0:
                print("El monto debe ser mayor a 0.")
                return
            ingreso["monto"] = nuevo_monto
        except ValueError:
            print("El monto debe ser un número válido.")
            return

    nuevo_origen = input(f"Nuevo origen [{ingreso['origen']}]: ").strip()
    if nuevo_origen != "":
        ingreso["origen"] = nuevo_origen

    nueva_descripcion = input(f"Nueva descripción [{ingreso['descripcion']}]: ").strip()
    if nueva_descripcion != "":
        ingreso["descripcion"] = nueva_descripcion

    guardar_ingresos()
    print("Ingreso editado exitosamente.")

def eliminarGasto():
    if not gastos:
        print("No hay gastos registrados para eliminar.")
        return

    print("Gastos registrados:")
    for i, gasto in enumerate(gastos, start=1):
        print(f"\n[{i}] Monto: {gasto['monto']}, Fecha: {gasto['fecha']}, Categoría: {gasto['categoria']}, Descripción: {gasto['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del gasto que desea eliminar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(gastos):
        print("Número inválido.")
        return

    gasto_eliminado = gastos.pop(opcion - 1)
    guardar_gastos()

    print("Gasto eliminado exitosamente.")
    print(f"Se eliminó: {gasto_eliminado['descripcion']} - ${gasto_eliminado['monto']}")

def eliminarGasto():
    if not gastos:
        print("No hay gastos registrados para eliminar.")
        return

    print("Gastos registrados:")
    for i, gasto in enumerate(gastos, start=1):
        print(f"\n[{i}] Monto: {gasto['monto']}, Fecha: {gasto['fecha']}, Categoría: {gasto['categoria']}, Descripción: {gasto['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del gasto que desea eliminar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(gastos):
        print("Número inválido.")
        return

    gasto_eliminado = gastos.pop(opcion - 1)
    guardar_gastos()

    print("Gasto eliminado exitosamente.")
    print(f"Se eliminó: {gasto_eliminado['descripcion']} - ${gasto_eliminado['monto']}")

####### JSON #######
def guardar_gastos():
    with open(RUTA_GASTOS, "w", encoding="utf-8") as archivo:
        json.dump(gastos, archivo, indent=4, ensure_ascii=False)

def guardar_ingresos():
    with open(RUTA_INGRESOS, "w", encoding="utf-8") as archivo:
        json.dump(ingresos, archivo, indent=4, ensure_ascii=False)

def cargar_gastos():
    global gastos
    try:
        with open(RUTA_GASTOS, "r", encoding="utf-8") as archivo:
            gastos = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        gastos = []

def cargar_ingresos():
    global ingresos
    try:
        with open(RUTA_INGRESOS, "r", encoding="utf-8") as archivo:
            ingresos = json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        ingresos = []