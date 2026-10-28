from django.core.management.base import BaseCommand, CommandError
from django.db import connection, DatabaseError
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "Comprueba conexión PostgreSQL y migraciones pendientes sin mostrar credenciales."

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW server_version")
                version = cursor.fetchone()[0]
            executor = MigrationExecutor(connection)
            pendientes = executor.migration_plan(executor.loader.graph.leaf_nodes())
        except DatabaseError:
            raise CommandError(
                "No se pudo verificar PostgreSQL. Revisá la URL, el acceso de red y la disponibilidad de la base."
            ) from None
        self.stdout.write(self.style.SUCCESS(f"Conexión PostgreSQL {version} verificada."))
        self.stdout.write(f"Migraciones pendientes: {len(pendientes)}.")
