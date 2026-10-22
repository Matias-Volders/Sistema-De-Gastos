"""Compatibilidad solo de lectura; Django actualiza el hash al iniciar sesión."""
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash
from werkzeug.security import check_password_hash


class WerkzeugLegacyHasher(BasePasswordHasher):
    algorithm = "werkzeug_legacy"

    def verify(self, password, encoded):
        try:
            prefijo, anterior = encoded.split("$", 1)
            return prefijo == self.algorithm and check_password_hash(anterior, password)
        except (ValueError, TypeError):
            return False

    def encode(self, password, salt):
        raise NotImplementedError("Las contraseñas nuevas se generan con Django.")

    def safe_summary(self, encoded):
        return {"algorithm": self.algorithm, "hash": mask_hash(encoded)}

    def must_update(self, encoded):
        return True
