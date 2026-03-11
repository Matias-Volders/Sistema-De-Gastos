import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash

import persistencia
import gastos as gastos_service
import ingresos as ingresos_service
import balance as balance_service


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

TEMPLATES_DIR = os.path.join(ROOT_DIR, "Front End")
STATIC_DIR = os.path.join(ROOT_DIR, "Front End")

app = Flask(
    __name__,
    template_folder=TEMPLATES_DIR,
    static_folder=STATIC_DIR
)

app.secret_key = "clave_super_secreta_cambiar"

persistencia.asegurar_archivos()
persistencia.cargar_gastos()
persistencia.cargar_ingresos()
persistencia.cargar_usuarios()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Tenés que iniciar sesión primero.")
            return redirect(url_for("iniciar_sesion"))
        return func(*args, **kwargs)
    return wrapper


def obtener_usuario_actual():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return persistencia.obtener_usuario_por_id(user_id)


@app.route("/")
def landing_page():
    if "user_id" in session:
        return redirect(url_for("panel"))
    return render_template("landingPage.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirmar_password = request.form.get("confirmar_password", "").strip()

        if not nombre or not email or not password or not confirmar_password:
            flash("Completá todos los campos.")
            return render_template("pagina_registrarse.html")

        if password != confirmar_password:
            flash("Las contraseñas no coinciden.")
            return render_template("pagina_registrarse.html")

        exito, respuesta = persistencia.registrar_usuario(nombre, email, password)

        if not exito:
            flash(respuesta)
            return render_template("pagina_registrarse.html")

        flash("Usuario registrado correctamente. Ahora iniciá sesión.")
        return redirect(url_for("iniciar_sesion"))

    return render_template("pagina_registrarse.html")


@app.route("/iniciarSesion", methods=["GET", "POST"])
def iniciar_sesion():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        usuario = persistencia.autenticar_usuario(email, password)

        if usuario is None:
            flash("Email o contraseña incorrectos.")
            return render_template("iniciarSesion.html")

        session["user_id"] = usuario["id"]
        session["user_nombre"] = usuario["nombre"]

        flash(f"Bienvenido, {usuario['nombre']}.")
        return redirect(url_for("panel"))

    return render_template("iniciarSesion.html")


@app.route("/cerrarSesion")
def cerrar_sesion():
    session.clear()
    flash("Sesión cerrada correctamente.")
    return redirect(url_for("iniciar_sesion"))


@app.route("/panel")
@login_required
def panel():
    usuario = obtener_usuario_actual()
    return render_template("panel.html", usuario=usuario)


@app.route("/gastos", methods=["GET", "POST"])
@login_required
def gastos():
    usuario = obtener_usuario_actual()

    if request.method == "POST":
        monto = request.form.get("monto", "").strip()
        categoria = request.form.get("categoria", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()

        if not monto or not categoria or not descripcion or not fecha:
            flash("Completá todos los campos del gasto.")
        else:
            try:
                gastos_service.crear_gasto(
                    session["user_id"],
                    monto,
                    categoria,
                    descripcion,
                    fecha
                )
                
                return redirect(url_for("gastos"))
            except ValueError:
                flash("El monto del gasto debe ser numérico.")

    gastos_usuario = gastos_service.obtener_gastos_usuario(session["user_id"])
    categorias = gastos_service.obtener_categorias_usuario(session["user_id"])

    return render_template(
        "funcionalidades/gastos.html",
        usuario=usuario,
        gastos=gastos_usuario,
        categorias=categorias,
        total_mes=None,
        mes_consultado=None,
        anio_consultado=None,
        categoria_consultada=None,
        total_categoria=None
    )

@app.route("/gastos/categoria", methods=["POST"])
@login_required
def gastos_categoria():
    usuario = obtener_usuario_actual()
    categorias = gastos_service.obtener_categorias_usuario(session["user_id"])
    categoria = request.form.get("categoria", "").strip()

    if not categoria:
        flash("Seleccioná una categoría.")
        gastos_usuario = gastos_service.obtener_gastos_usuario(session["user_id"])

        return render_template(
            "funcionalidades/gastos.html",
            usuario=usuario,
            gastos=gastos_usuario,
            categorias=categorias,
            total_mes=None,
            mes_consultado=None,
            anio_consultado=None,
            categoria_consultada=None,
            total_categoria=None
        )

    gastos_filtrados = gastos_service.obtener_gastos_por_categoria(
        session["user_id"],
        categoria
    )

    total_categoria = gastos_service.total_gastos_por_categoria(
        session["user_id"],
        categoria
    )

    return render_template(
        "funcionalidades/gastos.html",
        usuario=usuario,
        gastos=gastos_filtrados,
        categorias=categorias,
        total_mes=None,
        mes_consultado=None,
        anio_consultado=None,
        categoria_consultada=categoria,
        total_categoria=total_categoria
    )


@app.route("/gastos/eliminar/<int:gasto_id>", methods=["POST"])
@login_required
def eliminar_gasto(gasto_id):
    gastos_service.eliminar_gasto(session["user_id"], gasto_id)
    return redirect(url_for("gastos"))

@app.route("/gastos/editar/<int:gasto_id>", methods=["GET", "POST"])
@login_required
def editar_gasto(gasto_id):
    usuario = obtener_usuario_actual()
    gasto = gastos_service.obtener_gasto_por_id(session["user_id"], gasto_id)

    if gasto is None:
        flash("No se encontró el gasto.")
        return redirect(url_for("gastos"))

    if request.method == "POST":
        monto = request.form.get("monto", "").strip()
        categoria = request.form.get("categoria", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()

        if not monto or not categoria or not descripcion or not fecha:
            flash("Completá todos los campos.")
            return render_template(
                "funcionalidades/editar_gasto.html",
                usuario=usuario,
                gasto=gasto
            )

        try:
            editado = gastos_service.editar_gasto(
                session["user_id"],
                gasto_id,
                monto,
                categoria,
                descripcion,
                fecha
            )

            if editado:
                flash("Gasto editado correctamente.")
            else:
                flash("No se pudo editar el gasto.")

            return redirect(url_for("gastos"))

        except ValueError:
            flash("El monto debe ser numérico.")
            return render_template(
                "funcionalidades/editar_gasto.html",
                usuario=usuario,
                gasto=gasto
            )

    return render_template(
        "funcionalidades/editar_gasto.html",
        usuario=usuario,
        gasto=gasto
    )

@app.route("/gastos/mensuales", methods=["POST"])
@login_required
def gastos_mensuales():
    usuario = obtener_usuario_actual()
    gastos_usuario = gastos_service.obtener_gastos_usuario(session["user_id"])
    categorias = gastos_service.obtener_categorias_usuario(session["user_id"])

    mes = request.form.get("mes", "").strip()
    anio = request.form.get("anio", "").strip()

    total_mes = None

    if not mes or not anio:
        flash("Ingresá mes y año.")
    else:
        try:
            total_mes = gastos_service.total_gastos_mensuales(
                session["user_id"],
                mes,
                anio
            )
        except ValueError:
            flash("Mes o año inválidos.")

    return render_template(
        "funcionalidades/gastos.html",
        usuario=usuario,
        gastos=gastos_usuario,
        categorias=categorias,
        total_mes=total_mes,
        mes_consultado=mes,
        anio_consultado=anio,
        categoria_consultada=None,
        total_categoria=None
    )


@app.route("/ingresos", methods=["GET", "POST"])
@login_required
def ingresos():
    usuario = obtener_usuario_actual()

    if request.method == "POST":
        monto = request.form.get("monto", "").strip()
        origen = request.form.get("origen", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()

        if not monto or not origen or not descripcion or not fecha:
            flash("Completá todos los campos del ingreso.")
        else:
            try:
                ingresos_service.crear_ingreso(
                    session["user_id"],
                    monto,
                    origen,
                    descripcion,
                    fecha
                )
                
                return redirect(url_for("ingresos"))
            except ValueError:
                flash("El monto del ingreso debe ser numérico.")

    ingresos_usuario = ingresos_service.obtener_ingresos_usuario(session["user_id"])

    return render_template(
        "funcionalidades/ingresos.html",
        usuario=usuario,
        ingresos=ingresos_usuario,
        total_ingresos_mes=None,
        mes_consultado=None,
        anio_consultado=None
    )

@app.route("/ingresos/mensuales", methods=["POST"])
@login_required
def ingresos_mensuales():
    usuario = obtener_usuario_actual()
    ingresos_usuario = ingresos_service.obtener_ingresos_usuario(session["user_id"])

    mes = request.form.get("mes", "").strip()
    anio = request.form.get("anio", "").strip()

    total_ingresos_mes = None

    if not mes or not anio:
        flash("Ingresá mes y año.")
    else:
        try:
            total_ingresos_mes = ingresos_service.total_ingresos_mensuales(
                session["user_id"],
                mes,
                anio
            )
        except ValueError:
            flash("Mes o año inválidos.")

    return render_template(
        "funcionalidades/ingresos.html",
        usuario=usuario,
        ingresos=ingresos_usuario,
        total_ingresos_mes=total_ingresos_mes,
        mes_consultado=mes,
        anio_consultado=anio
    )


@app.route("/ingresos/eliminar/<int:ingreso_id>", methods=["POST"])
@login_required
def eliminar_ingreso(ingreso_id):
    ingresos_service.eliminar_ingreso(session["user_id"], ingreso_id)
    return redirect(url_for("ingresos"))

@app.route("/ingresos/editar/<int:ingreso_id>", methods=["GET", "POST"])
@login_required
def editar_ingreso(ingreso_id):
    usuario = obtener_usuario_actual()
    ingreso = ingresos_service.obtener_ingreso_por_id(session["user_id"], ingreso_id)

    if ingreso is None:
        flash("No se encontró el ingreso.")
        return redirect(url_for("ingresos"))

    if request.method == "POST":
        monto = request.form.get("monto", "").strip()
        origen = request.form.get("origen", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()

        if not monto or not origen or not descripcion or not fecha:
            flash("Completá todos los campos.")
            return render_template(
                "funcionalidades/editar_ingreso.html",
                usuario=usuario,
                ingreso=ingreso
            )

        try:
            editado = ingresos_service.editar_ingreso(
                session["user_id"],
                ingreso_id,
                monto,
                origen,
                descripcion,
                fecha
            )

            if editado:
                flash("Ingreso editado correctamente.")
            else:
                flash("No se pudo editar el ingreso.")

            return redirect(url_for("ingresos"))

        except ValueError:
            flash("El monto debe ser numérico.")
            return render_template(
                "funcionalidades/editar_ingreso.html",
                usuario=usuario,
                ingreso=ingreso
            )

    return render_template(
        "funcionalidades/editar_ingreso.html",
        usuario=usuario,
        ingreso=ingreso
    )

@app.route("/balance")
@login_required
def balance():
    usuario = obtener_usuario_actual()
    resumen = balance_service.calcular_balance(session["user_id"])

    return render_template(
        "funcionalidades/balance.html",
        usuario=usuario,
        total_ingresos=resumen["total_ingresos"],
        total_gastos=resumen["total_gastos"],
        balance=resumen["balance"],
        total_ingresos_mes=None,
        total_gastos_mes=None,
        balance_mes=None,
        mes_consultado=None,
        anio_consultado=None
    )

@app.route("/balance/mensual", methods=["POST"])
@login_required
def balance_mensual():
    usuario = obtener_usuario_actual()
    resumen = balance_service.calcular_balance(session["user_id"])

    mes = request.form.get("mes", "").strip()
    anio = request.form.get("anio", "").strip()

    total_ingresos_mes = None
    total_gastos_mes = None
    balance_mes = None

    if not mes or not anio:
        flash("Ingresá mes y año.")
    else:
        try:
            resumen_mensual = balance_service.calcular_balance_mensual(
                session["user_id"],
                mes,
                anio
            )

            total_ingresos_mes = resumen_mensual["total_ingresos_mes"]
            total_gastos_mes = resumen_mensual["total_gastos_mes"]
            balance_mes = resumen_mensual["balance_mes"]

        except ValueError:
            flash("Mes o año inválidos.")

    return render_template(
        "funcionalidades/balance.html",
        usuario=usuario,
        total_ingresos=resumen["total_ingresos"],
        total_gastos=resumen["total_gastos"],
        balance=resumen["balance"],
        total_ingresos_mes=total_ingresos_mes,
        total_gastos_mes=total_gastos_mes,
        balance_mes=balance_mes,
        mes_consultado=mes,
        anio_consultado=anio
    )

