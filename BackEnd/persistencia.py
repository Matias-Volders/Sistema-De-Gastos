import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_DIR = os.path.join(BASE_DIR, "Datos")

RUTA_GASTOS = os.path.join(DATOS_DIR, "gastos.json")
RUTA_INGRESOS = os.path.join(DATOS_DIR, "ingresos.json")

gastos = []
ingresos = []

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