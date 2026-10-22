from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password


class RegistroForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=150)
    email = forms.EmailField(label="Correo electrónico", max_length=254)
    password = forms.CharField(label="Contraseña", strip=False, max_length=256,
                               widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    confirmar_password = forms.CharField(label="Confirmar contraseña", strip=False, max_length=256,
                                         widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def clean_email(self):
        return self.cleaned_data["email"].lower()

    def clean(self):
        datos = super().clean()
        password = datos.get("password")
        if password and datos.get("confirmar_password") and password != datos["confirmar_password"]:
            self.add_error("confirmar_password", "Las contraseñas no coinciden.")
        if password:
            usuario = get_user_model()(email=datos.get("email", ""), nombre=datos.get("nombre", ""))
            try:
                validate_password(password, usuario)
            except forms.ValidationError as exc:
                self.add_error("password", exc)
        return datos


class InicioSesionForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico", max_length=254)
    password = forms.CharField(label="Contraseña", strip=False, max_length=256,
                               widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
