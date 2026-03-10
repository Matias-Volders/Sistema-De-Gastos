from flask import Flask, render_template, request, redirect, url_for
import persistencia
import gastos
import ingresos
import balance

app = Flask(
    __name__,
    template_folder="../Front End",
    static_folder="../Front End"
)

persistencia.cargar_gastos()
persistencia.cargar_ingresos()


@app.route("/")
def landing():
    return render_template("landingPage.html")


@app.route("/iniciar-sesion")
def iniciar_sesion():
    return render_template("iniciarSesion.html")


@app.route("/panel")
def panel():
    return render_template("panel.html")


@app.route("/gastos")
def pagina_gastos():
    lista_gastos = gastos.obtener_gastos()
    return render_template(
        "funcionalidades/gastos.html",
        gastos_lista=lista_gastos,
        categorias_resultado=None
    )


@app.route("/gastos/registrar", methods=["POST"])
def registrar_gasto():
    monto = request.form["monto"]
    categoria = request.form["categoria"]
    descripcion = request.form["descripcion"]

    gastos.registrar_gasto_web(monto, categoria, descripcion)
    return redirect(url_for("pagina_gastos"))


@app.route("/gastos/editar", methods=["POST"])
def editar_gasto():
    indice = request.form["indice"]
    monto = request.form["monto"]
    categoria = request.form["categoria"]
    descripcion = request.form["descripcion"]

    gastos.editar_gasto_web(indice, monto, categoria, descripcion)
    return redirect(url_for("pagina_gastos"))


@app.route("/gastos/eliminar", methods=["POST"])
def eliminar_gasto():
    indice = request.form["indice"]
    gastos.eliminar_gasto_web(indice)
    return redirect(url_for("pagina_gastos"))

@app.route("/gastos/mensuales", methods=["POST"])
def total_gastos_mensuales():
    mes = request.form["mes"]
    anio = request.form["anio"]

    total = gastos.total_gastos_mensuales(mes, anio)
    lista_gastos = gastos.obtener_gastos()

    return render_template(
        "funcionalidades/gastos.html",
        gastos_lista=lista_gastos,
        total_gastos=total,
        mes_consultado=mes,
        anio_consultado=anio,
        categorias_resultado=None
    )

@app.route("/gastos/categoria", methods=["POST"])
def gastos_categoria():
    mes = request.form["mes"]
    anio = request.form["anio"]

    lista_gastos = gastos.obtener_gastos()
    categorias_resultado = gastos.gastos_por_categoria_mensual_web(mes, anio)

    return render_template(
        "funcionalidades/gastos.html",
        gastos_lista=lista_gastos,
        categorias_resultado=categorias_resultado,
        mes_consultado=mes,
        anio_consultado=anio
    )


@app.route("/ingresos")
def pagina_ingresos():
    lista_ingresos = ingresos.obtener_ingresos()
    return render_template(
        "funcionalidades/ingresos.html",
        ingresos_lista=lista_ingresos
    )


@app.route("/ingresos/registrar", methods=["POST"])
def registrar_ingreso():
    monto = request.form["monto"]
    origen = request.form["origen"]
    descripcion = request.form["descripcion"]

    ingresos.registrar_ingreso_web(monto, origen, descripcion)
    return redirect(url_for("pagina_ingresos"))


@app.route("/ingresos/editar", methods=["POST"])
def editar_ingreso():
    indice = request.form["indice"]
    monto = request.form["monto"]
    origen = request.form["origen"]
    descripcion = request.form["descripcion"]

    ingresos.editar_ingreso_web(indice, monto, origen, descripcion)
    return redirect(url_for("pagina_ingresos"))


@app.route("/ingresos/eliminar", methods=["POST"])
def eliminar_ingreso():
    indice = request.form["indice"]
    ingresos.eliminar_ingreso_web(indice)
    return redirect(url_for("pagina_ingresos"))


@app.route("/balance")
def pagina_balance():
    balance_total = balance.calcular_balance_total_web()

    return render_template(
        "funcionalidades/balance.html",
        balance_total=balance_total,
        balance_mensual=None,
        categorias_resultado=None
    )


@app.route("/balance/mensual", methods=["POST"])
def balance_mensual():
    mes = request.form["mes"]
    anio = request.form["anio"]

    balance_total = balance.calcular_balance_total_web()
    balance_mes = balance.balance_mensual_web(mes, anio)
    categorias_resultado = gastos.gastos_por_categoria_mensual_web(mes, anio)

    return render_template(
        "funcionalidades/balance.html",
        balance_total=balance_total,
        balance_mensual=balance_mes,
        categorias_resultado=categorias_resultado,
        mes_consultado=mes,
        anio_consultado=anio
    )



if __name__ == "__main__":
    app.run(debug=True)