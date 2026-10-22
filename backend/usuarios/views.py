from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST

from backend.usuarios import services
from backend.usuarios.forms import InicioSesionForm, RegistroForm


@require_http_methods(["GET"])
def landing_page(request):
    if request.user.is_authenticated:
        return redirect("panel")
    return render(request, "landingPage.html")


@sensitive_post_parameters("password", "confirmar_password")
@require_http_methods(["GET", "POST"])
def registro(request):
    if request.user.is_authenticated:
        return redirect("panel")
    form = RegistroForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            services.registrar_usuario(
                nombre=form.cleaned_data["nombre"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
        except ValidationError as exc:
            form.add_error(None, exc.messages)
        else:
            messages.success(request, "Usuario registrado. Ahora iniciá sesión.")
            return redirect("iniciar_sesion")
    return render(request, "usuarios/registro.html", {"form": form})


@sensitive_post_parameters("password")
@require_http_methods(["GET", "POST"])
def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect("panel")
    form = InicioSesionForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        usuario = authenticate(request, username=form.cleaned_data["email"],
                               password=form.cleaned_data["password"])
        if usuario is not None:
            login(request, usuario)
            return redirect("panel")
        form.add_error(None, "Correo o contraseña incorrectos.")
    return render(request, "usuarios/login.html", {"form": form})


@require_POST
def cerrar_sesion(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("iniciar_sesion")


@login_required
@require_http_methods(["GET"])
def panel(request):
    return render(request, "panel.html", {"usuario": request.user})
