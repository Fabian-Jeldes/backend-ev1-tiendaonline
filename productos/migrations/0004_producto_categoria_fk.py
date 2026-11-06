"""
Migración 0004 — PASO 3 de 3: dejar la estructura final.

  1. Borra la columna antigua de texto "categoria" (ya se copió en el paso 2).
  2. Renombra "categoria_ref" a "categoria" (la columna en MySQL queda como categoria_id).
  3. La vuelve OBLIGATORIA (NOT NULL), con on_delete=PROTECT y related_name='productos'.

Resultado en MySQL:
  productos_producto.categoria_id  BIGINT NOT NULL  FOREIGN KEY -> productos_categoria.id
  productos_producto.marca_id      BIGINT NULL      FOREIGN KEY -> productos_marca.id
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0003_poblar_categorias_marcas'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='categoria',
        ),
        migrations.RenameField(
            model_name='producto',
            old_name='categoria_ref',
            new_name='categoria',
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='productos',
                to='productos.categoria',
                verbose_name='Categoría',
            ),
        ),
    ]
