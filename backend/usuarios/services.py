"""Registro de usuarios: validación, protección de contraseña y persistencia."""
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

from backend.usuarios import repository
from backend.usuarios.forms import RegistroForm


def registrar_usuario(nombre, email, password):
    formulario = RegistroForm({
        "nombre": nombre,
        "email": email,
        "password": password,
        "confirmar_password": password,
    })
    if not formulario.is_valid():
        raise ValidationError(formulario.errors.as_data())
    datos = formulario.cleaned_data
    return repository.crear_usuario(
        nombre=datos["nombre"],
        email=datos["email"],
        password_hash=make_password(datos["password"]),
    )
