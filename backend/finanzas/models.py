from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Lower, Trim
from decimal import Decimal


class Categoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="categorias")
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = "categoria"
        ordering = ["nombre", "id"]
        constraints = [
            models.UniqueConstraint(Lower(Trim("nombre")), "usuario", name="categoria_nombre_unico_por_usuario"),
            # Permite una FK compuesta que exija el mismo propietario en el registro financiero.
            models.UniqueConstraint(fields=["id", "usuario"], name="categoria_id_usuario_unico"),
            models.CheckConstraint(condition=~models.Q(nombre__regex=r"^\s*$"), name="categoria_nombre_no_vacio"),
        ]

    def clean(self):
        super().clean()
        self.nombre = self.nombre.strip()

    def __str__(self):
        return self.nombre


class Ingreso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ingresos")
    monto = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    fecha = models.DateField()
    descripcion = models.CharField(max_length=500)
    origen = models.CharField(max_length=150)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ingreso"
        ordering = ["-fecha", "-id"]
        indexes = [models.Index(fields=["usuario", "-fecha", "-id"], name="ingreso_usuario_fecha")]
        constraints = [
            models.CheckConstraint(condition=models.Q(monto__gt=0, monto__lt=Decimal("1000000000000")), name="ingreso_monto_valido"),
            models.CheckConstraint(condition=~models.Q(descripcion__regex=r"^\s*$"), name="ingreso_descripcion_no_vacia"),
            models.CheckConstraint(condition=~models.Q(origen__regex=r"^\s*$"), name="ingreso_origen_no_vacio"),
        ]


class Egreso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="egresos")
    monto = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    fecha = models.DateField()
    descripcion = models.CharField(max_length=500)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="egresos")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "egreso"
        ordering = ["-fecha", "-id"]
        indexes = [
            models.Index(fields=["usuario", "-fecha", "-id"], name="egreso_usuario_fecha"),
            models.Index(fields=["usuario", "categoria", "fecha"], name="egreso_usuario_categoria_fecha"),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(monto__gt=0, monto__lt=Decimal("1000000000000")), name="egreso_monto_valido"),
            models.CheckConstraint(condition=~models.Q(descripcion__regex=r"^\s*$"), name="egreso_descripcion_no_vacia"),
        ]

    def clean(self):
        super().clean()
        if self.categoria_id and self.usuario_id and self.categoria.usuario_id != self.usuario_id:
            raise ValidationError({"categoria": "La categoría debe pertenecer al mismo usuario."})
