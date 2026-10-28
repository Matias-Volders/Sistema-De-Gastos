from django.db import IntegrityError, transaction
from backend.finanzas.models import Categoria
from backend.tests.base import BaseDatosTestCase


class CategoriaTests(BaseDatosTestCase):
    def test_nombre_unico_por_usuario_sin_mayusculas_ni_espacios_exteriores(self):
        Categoria.objects.create(usuario=self.uno, nombre="Comida")
        for nombre in ("comida", " COMIDA "):
            with self.assertRaises(IntegrityError), transaction.atomic():
                Categoria.objects.create(usuario=self.uno, nombre=nombre)
        Categoria.objects.create(usuario=self.dos, nombre="Comida")
        self.assertEqual(Categoria.objects.count(), 2)

    def test_nombre_vacio_rechazado_por_la_base(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Categoria.objects.create(usuario=self.uno, nombre="  ")

    def test_categorias_con_acentos_se_reutilizan(self):
        from backend.finanzas.repository import obtener_o_crear_categoria
        primera = obtener_o_crear_categoria(self.uno.pk, "Alimentación")
        segunda = obtener_o_crear_categoria(self.uno.pk, " ALIMENTACIÓN ")
        self.assertEqual(primera.pk, segunda.pk)
