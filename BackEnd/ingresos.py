from datetime import datetime
import persistencia

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
    }

    persistencia.ingresos.append(ingreso)
    persistencia.guardar_ingresos()
    print("Ingreso registrado exitosamente.")

def mostrarIngresos():
    if not persistencia.ingresos:
        print("No hay ingresos registrados.")
        return

    print("Ingresos Registrados:")
    for i, ingreso in enumerate(persistencia.ingresos, start=1):
        print(f"\n[{i}] Monto: {ingreso['monto']}, Fecha: {ingreso['fecha']}, Origen: {ingreso['origen']}, Descripción: {ingreso['descripcion']}")

def editarIngreso():
    if not persistencia.ingresos:
        print("No hay ingresos registrados para editar.")
        return

    print("Ingresos registrados:")
    for i, ingreso in enumerate(persistencia.ingresos, start=1):
        print(f"\n[{i}] Monto: {ingreso['monto']}, Fecha: {ingreso['fecha']}, Origen: {ingreso['origen']}, Descripción: {ingreso['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del ingreso que quiere editar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(persistencia.ingresos):
        print("Número inválido.")
        return

    ingreso = persistencia.ingresos[opcion - 1]

    nuevo_monto = input(f"Nuevo monto [{ingreso['monto']}]: ").strip()
    if nuevo_monto != "":
        ingreso["monto"] = float(nuevo_monto)

    nuevo_origen = input(f"Nuevo origen [{ingreso['origen']}]: ").strip()
    if nuevo_origen != "":
        ingreso["origen"] = nuevo_origen

    nueva_descripcion = input(f"Nueva descripción [{ingreso['descripcion']}]: ").strip()
    if nueva_descripcion != "":
        ingreso["descripcion"] = nueva_descripcion

    persistencia.guardar_ingresos()
    print("Ingreso editado exitosamente.")

def eliminarIngreso():
    if not persistencia.ingresos:
        print("No hay ingresos registrados para eliminar.")
        return

    print("Ingresos registrados:")
    for i, ingreso in enumerate(persistencia.ingresos, start=1):
        print(f"\n[{i}] Monto: {ingreso['monto']}, Fecha: {ingreso['fecha']}, Origen: {ingreso['origen']}, Descripción: {ingreso['descripcion']}")

    try:
        opcion = int(input("\nIngrese el número del ingreso que desea eliminar: "))
    except ValueError:
        print("Debe ingresar un número válido.")
        return

    if opcion < 1 or opcion > len(persistencia.ingresos):
        print("Número inválido.")
        return

    ingreso_eliminado = persistencia.ingresos.pop(opcion - 1)
    persistencia.guardar_ingresos()

    print("Ingreso eliminado exitosamente.")
    print(f"Se eliminó: {ingreso_eliminado['descripcion']} - ${ingreso_eliminado['monto']}")


def obtener_ingresos():
    return persistencia.ingresos

def registrar_ingreso_web(monto, origen, descripcion):
    ingreso = {
        "monto": float(monto),
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "origen": origen,
        "descripcion": descripcion
    }
    persistencia.ingresos.append(ingreso)
    persistencia.guardar_ingresos()

def editar_ingreso_web(indice, monto, origen, descripcion):
    indice = int(indice)

    if indice < 0 or indice >= len(persistencia.ingresos):
        return False

    persistencia.ingresos[indice]["monto"] = float(monto)
    persistencia.ingresos[indice]["origen"] = origen
    persistencia.ingresos[indice]["descripcion"] = descripcion
    persistencia.guardar_ingresos()
    return True

def eliminar_ingreso_web(indice):
    indice = int(indice)

    if indice < 0 or indice >= len(persistencia.ingresos):
        return False

    persistencia.ingresos.pop(indice)
    persistencia.guardar_ingresos()
    return True