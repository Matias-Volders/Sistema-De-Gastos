import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATOS_DIR = os.path.join(BASE_DIR, "Datos")


RUTA_USUARIOS = os.path.join(DATOS_DIR, "usuarios.json")
RUTA_GASTOS = os.path.join(DATOS_DIR, "gastos.json")
RUTA_INGRESOS = os.path.join(DATOS_DIR, "ingresos.json")

gastos = []
ingresos = []
usuarios = []


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

#============== USUARIOS =================

def asegurar_archivos():
    os.makedirs(DATOS_DIR, exist_ok=True)

    for ruta in [RUTA_USUARIOS, RUTA_GASTOS, RUTA_INGRESOS]:
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as archivo:
                json.dump([], archivo, indent=4, ensure_ascii=False)


def leer_json(ruta):
    asegurar_archivos()

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def escribir_json(ruta, datos):
    asegurar_archivos()

    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)


def generar_id(lista):
    if not lista:
        return 1
    return max(item.get("id", 0) for item in lista) + 1

def cargar_usuarios():
    global usuarios
    usuarios = leer_json(RUTA_USUARIOS)
    return usuarios

def guardar_usuarios():
    global usuarios
    escribir_json(RUTA_USUARIOS, usuarios)


def obtener_usuario_por_id(user_id):
    global usuarios
    if not usuarios:
        cargar_usuarios()

    for usuario in usuarios:
        if usuario.get("id") == user_id:
            return usuario
    return None


def obtener_usuario_por_email(email):
    global usuarios
    if not usuarios:
        cargar_usuarios()

    email = email.strip().lower()

    for usuario in usuarios:
        if usuario.get("email", "").lower() == email:
            return usuario
    return None


def registrar_usuario(nombre, email, password):
    global usuarios
    cargar_usuarios()

    nombre = nombre.strip()
    email = email.strip().lower()
    password = password.strip()

    if not nombre or not email or not password:
        return False, "Todos los campos son obligatorios."

    if obtener_usuario_por_email(email) is not None:
        return False, "Ya existe un usuario con ese email."

    nuevo_usuario = {
        "id": generar_id(usuarios),
        "nombre": nombre,
        "email": email,
        "password": generate_password_hash(password)
    }

    usuarios.append(nuevo_usuario)
    guardar_usuarios()

    return True, nuevo_usuario


def autenticar_usuario(email, password):
    usuario = obtener_usuario_por_email(email)

    if usuario is None:
        return None

    if check_password_hash(usuario["password"], password):
        return usuario

    return None


# =========================
# CARGA INICIAL
# =========================

asegurar_archivos()
cargar_gastos()
cargar_ingresos()
cargar_usuarios()