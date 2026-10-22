from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from backend.core.importacion import ejecutar_importacion
from backend.core.legacy import cargar_origen, ErrorImportacion


class Command(BaseCommand):
    help = "Valida JSON anteriores; simula por defecto. --aplicar respalda e importa en una transacción."

    def add_arguments(self, parser):
        parser.add_argument("--origen", type=Path, default=settings.DATA_DIR)
        parser.add_argument("--respaldo-en", type=Path)
        modo = parser.add_mutually_exclusive_group()
        modo.add_argument("--aplicar", action="store_true")
        modo.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        try:
            datos = cargar_origen(options["origen"])
            resultado = ejecutar_importacion(
                datos, aplicar=options["aplicar"], respaldo_en=options["respaldo_en"]
            )
        except ErrorImportacion as exc:
            raise CommandError(str(exc)) from None
        except (DatabaseError, OSError):
            raise CommandError(
                "No se pudo completar la importación. Revisá conexión, migraciones y permisos del respaldo. "
                "No se confirma ninguna carga parcial."
            ) from None
        nuevas = resultado["nuevas"]
        self.stdout.write(
            f"Altas {'realizadas' if resultado['aplicado'] else 'previstas'}: "
            f"usuarios={nuevas['usuarios']}, ingresos={nuevas['ingresos']}, egresos={nuevas['egresos']}."
        )
        if resultado["aplicado"]:
            self.stdout.write(self.style.SUCCESS("Importación confirmada; cantidades y totales conciliados por usuario y mes."))
            self.stdout.write(f"Respaldo del origen: {resultado['respaldo']}")
        else:
            self.stdout.write("Simulación: no se escribieron filas ni se generó respaldo. Usá --aplicar para importar.")
