from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from backend.config.database import configurar_postgres


class ConfiguracionPostgresTests(SimpleTestCase):
    def test_exige_postgres_y_configuracion_explicita(self):
        for url in ("", "sqlite:///datos.sqlite3", "postgresql://"):
            with self.assertRaises(ImproperlyConfigured):
                configurar_postgres(url)

    def test_neon_conserva_tls_y_decodifica_clave(self):
        config = configurar_postgres(
            "postgresql://demo:clave%40ficticia@ejemplo.neon.tech/gastos?sslmode=require&channel_binding=require"
        )
        self.assertEqual(config["PASSWORD"], "clave@ficticia")
        self.assertEqual(config["OPTIONS"]["sslmode"], "require")
        self.assertEqual(config["OPTIONS"]["channel_binding"], "require")
        self.assertTrue(config["DISABLE_SERVER_SIDE_CURSORS"])

    def test_rechaza_conexion_remota_sin_tls(self):
        with self.assertRaises(ImproperlyConfigured):
            configurar_postgres("postgresql://demo:demo@ejemplo.test/base?sslmode=disable")

    def test_error_no_revela_url_ni_password(self):
        with self.assertRaises(ImproperlyConfigured) as resultado:
            configurar_postgres("postgresql://demo:clave-ficticia@localhost/base?opcion_inexistente=1")
        self.assertNotIn("clave-ficticia", str(resultado.exception))
