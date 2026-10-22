from decimal import Decimal
from django import forms


class MovimientoForm(forms.Form):
    monto = forms.DecimalField(label="Monto", max_digits=14, decimal_places=2,
                               min_value=Decimal("0.01"),
                               widget=forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}))
    descripcion = forms.CharField(label="Descripción", max_length=500)
    fecha = forms.DateField(label="Fecha", input_formats=["%Y-%m-%d"],
                           widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}))


class GastoForm(MovimientoForm):
    categoria = forms.CharField(label="Categoría", max_length=100)
    field_order = ["monto", "categoria", "descripcion", "fecha"]


class IngresoForm(MovimientoForm):
    origen = forms.CharField(label="Origen", max_length=150)
    field_order = ["monto", "origen", "descripcion", "fecha"]


class PeriodoForm(forms.Form):
    mes = forms.IntegerField(label="Mes", min_value=1, max_value=12)
    anio = forms.IntegerField(label="Año", min_value=1, max_value=9999)


class CategoriaForm(forms.Form):
    categoria = forms.ChoiceField(label="Categoría")

    def __init__(self, *args, categorias=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].choices = [("", "Seleccionar")] + [(c, c) for c in categorias]
