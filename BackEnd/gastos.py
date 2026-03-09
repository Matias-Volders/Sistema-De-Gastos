from datetime import datetime
import persistencia

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

    persistencia.gastos.append(gasto)
    persistencia.guardar_gastos()
    print("Gasto registrado exitosamente.")

def mostrarGastos():
    if not persistencia.gastos:
        print("No hay gastos registrados.")
        return
    print("Gastos Registrados:")
    for i, gasto in enumerate(persistencia.gastos, start=1):
        print(f"\n[{i}] Monto: {gasto['monto']}, Fecha: {gasto['fecha']}, Categoría: {gasto['categoria']}, Descripción: {gasto['descripcion']}")

def editarGasto():
    if not persistencia.gastos:
        print("No hay gastos registrados para editar.")
        return

    print("Gastos registrados:")
    for i, gasto in enumerate(persistencia.gastos, start=1):
        print(f"\n[{i}] Monto: {gasto['monto']}, Fecha: {gasto['fecha']}, Categoría: {gasto['categoria']}, Descripción: {gasto['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del gasto que quiere editar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(persistencia.gastos):
        print("Número inválido.")
        return

    gasto = persistencia.gastos[opcion - 1]

    nuevo_monto = input(f"Nuevo monto [{gasto['monto']}]: ").strip()
    if nuevo_monto != "":
        gasto["monto"] = float(nuevo_monto)

    nueva_categoria = input(f"Nueva categoría [{gasto['categoria']}]: ").strip()
    if nueva_categoria != "":
        gasto["categoria"] = nueva_categoria

    nueva_descripcion = input(f"Nueva descripción [{gasto['descripcion']}]: ").strip()
    if nueva_descripcion != "":
        gasto["descripcion"] = nueva_descripcion

    persistencia.guardar_gastos()
    print("Gasto editado exitosamente.")

def eliminarGasto():
    if not persistencia.gastos:
        print("No hay gastos registrados para eliminar.")
        return

    print("Gastos registrados:")
    for i, gasto in enumerate(persistencia.gastos, start=1):
        print(f"\n[{i}] Monto: {gasto['monto']}, Fecha: {gasto['fecha']}, Categoría: {gasto['categoria']}, Descripción: {gasto['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del gasto que desea eliminar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(persistencia.gastos):
        print("Número inválido.")
        return

    gasto_eliminado = persistencia.gastos.pop(opcion - 1)
    persistencia.guardar_gastos()

    print("Gasto eliminado exitosamente.")
    print(f"Se eliminó: {gasto_eliminado['descripcion']} - ${gasto_eliminado['monto']}")

def gastosPorCategoria():
    categorias = {}
    for gasto in persistencia.gastos:
        categoria = gasto["categoria"]
        monto = gasto["monto"]
        categorias[categoria] = categorias.get(categoria, 0) + monto

    print("Gastos por Categoría:")
    for categoria, monto in categorias.items():
        print(f"{categoria}: {monto}")

#CONEXION CON LA WEB

def obtener_gastos():
    return persistencia.gastos

def registrar_gasto_web(monto, categoria, descripcion):
    gasto = {
        "monto": float(monto),
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "categoria": categoria,
        "descripcion": descripcion
    }
    persistencia.gastos.append(gasto)
    persistencia.guardar_gastos()

def editar_gasto_web(indice, monto, categoria, descripcion):
    indice = int(indice)

    if indice < 0 or indice >= len(persistencia.gastos):
        return False

    persistencia.gastos[indice]["monto"] = float(monto)
    persistencia.gastos[indice]["categoria"] = categoria
    persistencia.gastos[indice]["descripcion"] = descripcion
    persistencia.guardar_gastos()
    return True

def eliminar_gasto_web(indice):
    indice = int(indice)

    if indice < 0 or indice >= len(persistencia.gastos):
        return False

    persistencia.gastos.pop(indice)
    persistencia.guardar_gastos()
    return True

def gastos_por_categoria_mensual_web(mes, anio):
    categorias = {}

    for gasto in persistencia.gastos:
        fecha = datetime.strptime(gasto["fecha"], "%d/%m/%Y %H:%M:%S")

        if fecha.month == int(mes) and fecha.year == int(anio):
            categoria = gasto["categoria"]
            monto = gasto["monto"]

            if categoria in categorias:
                categorias[categoria] += monto
            else:
                categorias[categoria] = monto

    return categorias