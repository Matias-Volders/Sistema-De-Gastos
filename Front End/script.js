function mostrarSeccion(seccionId) {
    const secciones = document.querySelectorAll("main section[id]");

    secciones.forEach(seccion => {
        seccion.style.display = "none";
    });

    const seccionElegida = document.getElementById(seccionId);

    if (seccionElegida) {
        seccionElegida.style.display = "block";
    }
}