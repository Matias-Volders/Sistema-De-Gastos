"""Lectura y respaldo del formato anterior. Nunca escribe en los JSON de origen."""
import hashlib
import json
import tempfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.hashers import identify_hasher
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from backend.finanzas.forms import GastoForm, IngresoForm


class ErrorImportacion(Exception):
    """Mensaje sin datos privados, apto para la salida del comando."""


@dataclass
class DatosAnteriores:
    usuarios: list
    gastos: list
    ingresos: list
    archivos: dict

    def respaldar(self, destino=None):
        base = Path(destino) if destino else settings.LOCAL_DIR / "backups"
        base.mkdir(parents=True, exist_ok=True)
        carpeta = Path(tempfile.mkdtemp(prefix="importacion-json-", dir=base))
        huellas = {}
        for nombre, contenido in self.archivos.items():
            (carpeta / nombre).write_bytes(contenido)
            huellas[nombre] = hashlib.sha256(contenido).hexdigest()
        (carpeta / "manifest.json").write_text(json.dumps(huellas, indent=2), encoding="utf-8")
        return carpeta


def _leer_lista(carpeta, coleccion, archivos):
    nombre = coleccion + ".json"
    try:
        contenido = (carpeta / nombre).read_bytes()
        filas = json.loads(contenido.decode("utf-8-sig"), parse_float=Decimal)
    except (OSError, ValueError, UnicodeError):
        raise ErrorImportacion(f"No se pudo leer {nombre}. Se requieren los tres archivos válidos.") from None
    if not isinstance(filas, list):
        raise ErrorImportacion(f"{nombre} debe contener una lista.")
    ids = set()
    for posicion, fila in enumerate(filas, start=1):
        if not isinstance(fila, dict) or type(fila.get("id")) is not int or not 1 <= fila["id"] <= 9223372036854775807:
            raise ErrorImportacion(f"{nombre}, fila {posicion}: ID inválido.")
        if fila["id"] in ids:
            raise ErrorImportacion(f"{nombre}, fila {posicion}: ID duplicado.")
        ids.add(fila["id"])
        campos = {"id", "nombre", "email", "password"} if coleccion == "usuarios" else {
            "id", "user_id", "monto", "fecha", "descripcion", "categoria" if coleccion == "gastos" else "origen"
        }
        if set(fila) != campos:
            raise ErrorImportacion(f"{nombre}, fila {posicion}: faltan campos o hay campos desconocidos; revisar antes de importar.")
    archivos[nombre] = contenido
    return filas


def adaptar_hash(encoded):
    if not isinstance(encoded, str) or not encoded:
        raise ValidationError("Hash no válido.")
    if encoded.startswith(("scrypt:", "pbkdf2:")):
        if len(encoded.split("$")) != 3:
            raise ValidationError("Hash legacy incompleto.")
        encoded = "werkzeug_legacy$" + encoded
    else:
        hasher = identify_hasher(encoded)
        if hasattr(hasher, "decode"):
            hasher.decode(encoded)
    if len(encoded) > 256:
        raise ValidationError("Hash demasiado largo.")
    return encoded


def cargar_origen(carpeta):
    carpeta = Path(carpeta)
    archivos = {}
    usuarios = _leer_lista(carpeta, "usuarios", archivos)
    gastos = _leer_lista(carpeta, "gastos", archivos)
    ingresos = _leer_lista(carpeta, "ingresos", archivos)
    usuarios_limpios = []
    correos = set()
    for posicion, fila in enumerate(usuarios, start=1):
        try:
            nombre = fila["nombre"].strip()
            email = fila["email"].strip().lower()
            validate_email(email)
            if not nombre or len(nombre) > 150 or len(email) > 254 or email in correos:
                raise ValueError()
            password = adaptar_hash(fila["password"])
        except (KeyError, TypeError, AttributeError, ValueError, ValidationError):
            raise ErrorImportacion(f"usuarios.json, fila {posicion}: datos inválidos o correo duplicado.") from None
        correos.add(email)
        usuarios_limpios.append({"id": fila["id"], "nombre": nombre, "email": email, "password": password})
    ids_usuario = {fila["id"] for fila in usuarios_limpios}
    colecciones = {}
    for coleccion, filas, formulario in (("gastos", gastos, GastoForm), ("ingresos", ingresos, IngresoForm)):
        limpios = []
        for posicion, fila in enumerate(filas, start=1):
            form = formulario(fila)
            propietario = fila.get("user_id")
            if type(propietario) is not int or propietario not in ids_usuario or not form.is_valid():
                raise ErrorImportacion(f"{coleccion}.json, fila {posicion}: campos inválidos o usuario inexistente.")
            limpios.append({"id": fila["id"], "usuario_id": propietario, **form.cleaned_data})
        colecciones[coleccion] = limpios
    # Exige una copia estable; detener la versión anterior antes de importar.
    try:
        if any((carpeta / nombre).read_bytes() != contenido for nombre, contenido in archivos.items()):
            raise ErrorImportacion("Los archivos cambiaron durante la lectura; detené la aplicación anterior.")
    except OSError:
        raise ErrorImportacion("No se pudo verificar la estabilidad del origen.") from None
    return DatosAnteriores(usuarios_limpios, colecciones["gastos"], colecciones["ingresos"], archivos)
