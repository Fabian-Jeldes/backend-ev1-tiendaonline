"""
Migración 0003 — PASO 2 de 3: migración de DATOS (no de estructura).

Usa RunPython para ejecutar código Python durante "migrate":
  1. Crea las 6 categorías que antes eran opciones fijas (choices).
  2. Recorre cada producto existente y conecta su texto antiguo
     (ej. "Audio") con la fila nueva de la tabla Categoria.
  3. Crea las marcas conocidas y se las asigna a los productos
     cuyo nombre contiene la marca (ej. "Auriculares Sony ..." -> Sony).

Importante: se usa apps.get_model(...) en vez de importar los modelos
directamente, porque la migración debe trabajar con la versión del modelo
que existía EN ESTE PUNTO del historial, no con la versión final.

También define la función inversa (deshacer), para que
"migrate productos 0002" pueda revertir el cambio sin perder datos.
"""

from django.db import migrations
from django.utils.text import slugify

# Las mismas categorías que existían como "choices" en la versión anterior.
CATEGORIAS = [
    ('Computación', 'Notebooks, PCs de escritorio y componentes.'),
    ('Monitores', 'Pantallas para gaming, oficina y diseño.'),
    ('Periféricos', 'Teclados, mouse y dispositivos de entrada.'),
    ('Audio', 'Audífonos, parlantes y micrófonos.'),
    ('Accesorios', 'Cables, soportes, mochilas y otros complementos.'),
    ('Videojuegos', 'Consolas, juegos y accesorios gamer.'),
]

# Marcas iniciales: (nombre, país de origen, sitio web).
MARCAS = [
    ('ASUS', 'Taiwán', 'https://www.asus.com'),
    ('Samsung', 'Corea del Sur', 'https://www.samsung.com'),
    ('Keychron', 'China', 'https://www.keychron.com'),
    ('Sony', 'Japón', 'https://www.sony.com'),
    ('Logitech', 'Suiza', 'https://www.logitech.com'),
    ('Razer', 'Estados Unidos', 'https://www.razer.com'),
]


def poblar(apps, schema_editor):
    Categoria = apps.get_model('productos', 'Categoria')
    Marca = apps.get_model('productos', 'Marca')
    Producto = apps.get_model('productos', 'Producto')

    # 1) Crear categorías. get_or_create evita duplicados si se ejecuta dos veces.
    #    El slug se calcula aquí porque el save() personalizado no existe en los modelos históricos.
    por_nombre = {}
    for nombre, descripcion in CATEGORIAS:
        categoria, _ = Categoria.objects.get_or_create(
            nombre=nombre,
            defaults={'slug': slugify(nombre), 'descripcion': descripcion},
        )
        por_nombre[nombre] = categoria

    # 2) Crear marcas.
    marcas = []
    for nombre, pais, web in MARCAS:
        marca, _ = Marca.objects.get_or_create(
            nombre=nombre, defaults={'pais_origen': pais, 'sitio_web': web},
        )
        marcas.append(marca)

    # 3) Conectar cada producto con su categoría y su marca.
    for producto in Producto.objects.all():
        texto = producto.categoria  # valor antiguo, ej: "Monitores"
        if texto not in por_nombre:
            # Si había una categoría escrita fuera de la lista, se crea igual para no perder el dato.
            por_nombre[texto], _ = Categoria.objects.get_or_create(
                nombre=texto, defaults={'slug': slugify(texto)},
            )
        producto.categoria_ref = por_nombre[texto]

        # Busca la marca dentro del nombre sin importar mayúsculas: "Teclado Keychron K2" -> Keychron
        nombre_minus = producto.nombre.lower()
        producto.marca = next((m for m in marcas if m.nombre.lower() in nombre_minus), None)

        producto.save(update_fields=['categoria_ref', 'marca'])


def deshacer(apps, schema_editor):
    """Inverso: copia el nombre de la categoría de vuelta a la columna de texto."""
    Producto = apps.get_model('productos', 'Producto')
    for producto in Producto.objects.select_related('categoria_ref'):
        if producto.categoria_ref_id:
            producto.categoria = producto.categoria_ref.nombre
            producto.save(update_fields=['categoria'])


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_categoria_marca'),
    ]

    operations = [
        migrations.RunPython(poblar, deshacer),
    ]
