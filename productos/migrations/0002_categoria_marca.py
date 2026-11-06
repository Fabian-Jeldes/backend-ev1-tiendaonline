"""
Migración 0002 — PASO 1 de 3: crear las tablas nuevas.

  - Crea las tablas productos_categoria y productos_marca.
  - Agrega a productos_producto dos columnas temporales/nuevas:
      * categoria_ref_id  (FK a categoría, por ahora permite NULL)
      * marca_id          (FK a marca, opcional)

Todavía NO se borra la columna antigua "categoria" (texto), porque
sus valores se necesitan en el paso 2 para saber a qué categoría
pertenece cada producto existente.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, unique=True, verbose_name='Nombre')),
                ('slug', models.SlugField(blank=True, max_length=60, unique=True, verbose_name='Slug (URL)')),
                ('descripcion', models.TextField(blank=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=60, unique=True, verbose_name='Nombre')),
                ('pais_origen', models.CharField(blank=True, max_length=60, verbose_name='País de origen')),
                ('sitio_web', models.URLField(blank=True, verbose_name='Sitio web oficial')),
            ],
            options={
                'verbose_name': 'Marca',
                'verbose_name_plural': 'Marcas',
                'ordering': ['nombre'],
            },
        ),
        # Columna temporal: se llama "categoria_ref" para no chocar con la columna de texto "categoria".
        migrations.AddField(
            model_name='producto',
            name='categoria_ref',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='productos.categoria',
            ),
        ),
        migrations.AddField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='productos',
                to='productos.marca',
                verbose_name='Marca',
            ),
        ),
    ]
