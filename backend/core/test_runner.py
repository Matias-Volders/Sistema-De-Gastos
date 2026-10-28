"""Evita ejecutar la suite SQL con la conexión operativa."""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.runner import DiscoverRunner


class PostgresTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        if not getattr(settings, "BASE_DE_PRUEBA_EXPLICITA", False):
            raise ImproperlyConfigured(
                "Usá --settings=backend.config.settings_test y DATABASE_TEST_URL "
                "hacia un PostgreSQL descartable, separado de tus datos."
            )
        return super().setup_databases(**kwargs)
