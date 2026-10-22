"""Usuario persistido: el correo es la credencial de acceso."""
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email.strip())

    def create_user(self, email, password=None, **extra_fields):
        if not email or not email.strip():
            raise ValueError("El correo es obligatorio.")
        usuario = self.model(email=email.strip().lower(), **extra_fields)
        usuario.set_password(password)
        usuario.full_clean()
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields["is_staff"] is not True or extra_fields["is_superuser"] is not True:
            raise ValueError("El superusuario debe tener permisos de administración.")
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=254)
    nombre = models.CharField(max_length=150)
    # Admite temporalmente hashes Werkzeug importados, más largos que los de Django.
    password = models.CharField(max_length=256)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre"]

    class Meta:
        db_table = "usuario"
        constraints = [
            models.UniqueConstraint(Lower("email"), name="usuario_email_unico_sin_mayusculas"),
        ]

    def clean(self):
        super().clean()
        self.email = self.email.strip().lower()
        self.nombre = self.nombre.strip()
        if not self.nombre:
            raise ValidationError({"nombre": "El nombre es obligatorio."})

    def __str__(self):
        return self.nombre

    def get_full_name(self):
        return self.nombre

    def get_short_name(self):
        return self.nombre
