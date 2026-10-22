from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("finanzas", "0002_egreso_ingreso")]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE egreso
                ADD CONSTRAINT egreso_categoria_del_usuario
                FOREIGN KEY (categoria_id, usuario_id)
                REFERENCES categoria (id, usuario_id)
                ON DELETE NO ACTION;
            """,
            reverse_sql="ALTER TABLE egreso DROP CONSTRAINT egreso_categoria_del_usuario;",
        ),
    ]
