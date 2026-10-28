document.addEventListener("submit", (event) => {
    if (event.target.matches("[data-confirm-delete]") &&
        !window.confirm("¿Querés eliminar este movimiento?")) {
        event.preventDefault();
    }
});
