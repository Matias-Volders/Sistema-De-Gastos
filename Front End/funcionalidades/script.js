function mostrarSeccion(seccionId) {
    const secciones = document.querySelectorAll("main section[id]");

    secciones.forEach(seccion => {
        seccion.style.display = "none";
    });

    document.getElementById(seccionId).style.display = "block";
}