"""Consultas de usuarios mediante ORM; no accede a archivos JSON."""
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from backend.usuarios.models import Usuario


def por_id(user_id):
    return Usuario.objects.filter(pk=user_id).first()


def por_email(email):
    return Usuario.objects.filter(email__iexact=email.strip()).first()


def crear_usuario(*, nombre, email, password_hash):
    try:
        with transaction.atomic():
            return Usuario.objects.create(nombre=nombre, email=email.strip().lower(), password=password_hash)
    except IntegrityError:
        if Usuario.objects.filter(email__iexact=email.strip()).exists():
            raise ValidationError("Ya existe un usuario con ese correo.") from None
        raise
