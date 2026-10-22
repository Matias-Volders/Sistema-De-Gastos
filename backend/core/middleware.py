from django.shortcuts import render
from django.db import OperationalError, InterfaceError


class ErroresPersistenciaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, (OperationalError, InterfaceError)):
            return render(request, "error_datos.html", status=503)
        return None
