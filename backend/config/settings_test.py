"""Las pruebas crean test_<base> usando una conexión PostgreSQL separada."""
import os
from pathlib import Path

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

from backend.config.database import configurar_postgres

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
url_pruebas = os.environ.get("DATABASE_TEST_URL", "")
config_pruebas = configurar_postgres(url_pruebas, "DATABASE_TEST_URL")
url_operativa = os.environ.get("DATABASE_URL")
if url_operativa:
    config_operativa = configurar_postgres(url_operativa)
    def destino(config):
        return (config["HOST"].replace("-pooler.", "."), config["PORT"], config["NAME"])
    if destino(config_operativa) == destino(config_pruebas):
        raise ImproperlyConfigured("DATABASE_TEST_URL debe apuntar a otra base o rama de prueba.")

# settings necesita una URL válida; restauramos el entorno después de importarlo.
os.environ["DATABASE_URL"] = url_pruebas
try:
    from backend.config.settings import *  # noqa: F403
finally:
    if url_operativa is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = url_operativa

DATABASES = {"default": config_pruebas}
BASE_DE_PRUEBA_EXPLICITA = True
DEBUG = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "backend.usuarios.hashers.WerkzeugLegacyHasher",
]
