import persistencia
from datetime import datetime


def crear_gasto(user_id, monto, categoria, descripcion, fecha):
    persistencia.cargar_gastos()

    nuevo_gasto = {
        "id": persistencia.generar_id(persistencia.gastos),
        "user_id": user_id,
        "monto": float(monto),
        "categoria": categoria.strip(),
        "descripcion": descripcion.strip(),
        "fecha": fecha
    }

    persistencia.gastos.append(nuevo_gasto)
    persistencia.guardar_gastos()
    return nuevo_gasto


def obtener_gastos_usuario(user_id):
    persistencia.cargar_gastos()

    gastos_usuario = [
        gasto for gasto in persistencia.gastos
        if gasto.get("user_id") == user_id
    ]

    return sorted(gastos_usuario, key=lambda x: x["fecha"], reverse=True)


def eliminar_gasto(user_id, gasto_id):
    persistencia.cargar_gastos()

    nuevos_gastos = []
    eliminado = False

    for gasto in persistencia.gastos:
        if gasto.get("id") == gasto_id and gasto.get("user_id") == user_id:
            eliminado = True
        else:
            nuevos_gastos.append(gasto)

    if eliminado:
        persistencia.gastos = nuevos_gastos
        persistencia.guardar_gastos()

    return eliminado


def total_gastos_usuario(user_id):
    gastos_usuario = obtener_gastos_usuario(user_id)
    return sum(gasto["monto"] for gasto in gastos_usuario)


def total_gastos_mensuales(user_id, mes, anio):
    gastos_usuario = obtener_gastos_usuario(user_id)
    total = 0

    for gasto in gastos_usuario:
        fecha_obj = datetime.strptime(gasto["fecha"], "%Y-%m-%d")
        if fecha_obj.month == int(mes) and fecha_obj.year == int(anio):
            total += gasto["monto"]

    return total

def obtener_gasto_por_id(user_id, gasto_id):
    persistencia.cargar_gastos()

    for gasto in persistencia.gastos:
        if gasto.get("id") == gasto_id and gasto.get("user_id") == user_id:
            return gasto

    return None


def editar_gasto(user_id, gasto_id, monto, categoria, descripcion, fecha):
    persistencia.cargar_gastos()

    for gasto in persistencia.gastos:
        if gasto.get("id") == gasto_id and gasto.get("user_id") == user_id:
            gasto["monto"] = float(monto)
            gasto["categoria"] = categoria.strip()
            gasto["descripcion"] = descripcion.strip()
            gasto["fecha"] = fecha

            persistencia.guardar_gastos()
            return True

    return False

def obtener_categorias_usuario(user_id):
    gastos_usuario = obtener_gastos_usuario(user_id)
    categorias = set()

    for gasto in gastos_usuario:
        categoria = gasto.get("categoria", "").strip()
        if categoria:
            categorias.add(categoria)

    return sorted(list(categorias))


def obtener_gastos_por_categoria(user_id, categoria):
    gastos_usuario = obtener_gastos_usuario(user_id)

    return [
        gasto for gasto in gastos_usuario
        if gasto.get("categoria", "").strip().lower() == categoria.strip().lower()
    ]


def total_gastos_por_categoria(user_id, categoria):
    gastos_categoria = obtener_gastos_por_categoria(user_id, categoria)
    return sum(gasto["monto"] for gasto in gastos_categoria)