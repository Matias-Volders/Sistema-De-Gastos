import persistencia


def crear_ingreso(user_id, monto, origen, descripcion, fecha):
    persistencia.cargar_ingresos()

    nuevo_ingreso = {
        "id": persistencia.generar_id(persistencia.ingresos),
        "user_id": user_id,
        "monto": float(monto),
        "origen": origen.strip(),
        "descripcion": descripcion.strip(),
        "fecha": fecha
    }

    persistencia.ingresos.append(nuevo_ingreso)
    persistencia.guardar_ingresos()
    return nuevo_ingreso


def obtener_ingresos_usuario(user_id):
    persistencia.cargar_ingresos()

    ingresos_usuario = [
        ingreso for ingreso in persistencia.ingresos
        if ingreso.get("user_id") == user_id
    ]

    return sorted(ingresos_usuario, key=lambda x: x["fecha"], reverse=True)


def eliminar_ingreso(user_id, ingreso_id):
    persistencia.cargar_ingresos()

    nuevos_ingresos = []
    eliminado = False

    for ingreso in persistencia.ingresos:
        if ingreso.get("id") == ingreso_id and ingreso.get("user_id") == user_id:
            eliminado = True
        else:
            nuevos_ingresos.append(ingreso)

    if eliminado:
        persistencia.ingresos = nuevos_ingresos
        persistencia.guardar_ingresos()

    return eliminado


def total_ingresos_usuario(user_id):
    ingresos_usuario = obtener_ingresos_usuario(user_id)
    return sum(ingreso["monto"] for ingreso in ingresos_usuario)

def obtener_ingreso_por_id(user_id, ingreso_id):
    persistencia.cargar_ingresos()

    for ingreso in persistencia.ingresos:
        if ingreso.get("id") == ingreso_id and ingreso.get("user_id") == user_id:
            return ingreso

    return None


def editar_ingreso(user_id, ingreso_id, monto, origen, descripcion, fecha):
    persistencia.cargar_ingresos()

    for ingreso in persistencia.ingresos:
        if ingreso.get("id") == ingreso_id and ingreso.get("user_id") == user_id:
            ingreso["monto"] = float(monto)
            ingreso["origen"] = origen.strip()
            ingreso["descripcion"] = descripcion.strip()
            ingreso["fecha"] = fecha

            persistencia.guardar_ingresos()
            return True

    return False