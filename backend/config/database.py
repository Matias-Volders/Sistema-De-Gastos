"""Traduce una URL PostgreSQL a configuración Django sin exponer credenciales."""
from django.core.exceptions import ImproperlyConfigured
from psycopg.conninfo import conninfo_to_dict
from psycopg import ProgrammingError, OperationalError


def configurar_postgres(url, nombre_variable="DATABASE_URL"):
    if not url:
        raise ImproperlyConfigured(
            f"Falta {nombre_variable}. Copiá .env.example a .env y configurá tu conexión PostgreSQL."
        )
    if not url.startswith(("postgresql://", "postgres://")):
        raise ImproperlyConfigured("DATABASE_URL debe ser una URL PostgreSQL.")
    try:
        parametros = conninfo_to_dict(url)
    except (ProgrammingError, OperationalError):
        raise ImproperlyConfigured("La URL PostgreSQL no tiene un formato válido.") from None
    requeridos = ("dbname", "host", "user")
    if any(not parametros.get(campo) for campo in requeridos):
        raise ImproperlyConfigured("La URL debe indicar base, host y usuario.")
    opciones = {
        clave: valor for clave, valor in parametros.items()
        if clave not in {"dbname", "host", "port", "user", "password"}
    }
    opciones.setdefault("connect_timeout", 10)
    local = parametros["host"] in {"localhost", "127.0.0.1", "::1"}
    opciones.setdefault("sslmode", "disable" if local else "require")
    if not local and opciones["sslmode"] not in {"require", "verify-ca", "verify-full"}:
        raise ImproperlyConfigured("La conexión remota a PostgreSQL debe usar TLS.")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parametros["dbname"],
        "HOST": parametros["host"],
        "PORT": parametros.get("port", "5432"),
        "USER": parametros["user"],
        "PASSWORD": parametros.get("password", ""),
        "OPTIONS": opciones,
        "CONN_MAX_AGE": 0,
        "CONN_HEALTH_CHECKS": True,
        # Compatible con el pool de conexiones de Neon.
        "DISABLE_SERVER_SIDE_CURSORS": True,
    }
