"""
=====================================================================
 productos/models.py — Modelo de datos relacional (Criterio 2.1.3)
=====================================================================

Cada clase de este archivo es una TABLA en MySQL y cada atributo es una
COLUMNA. Django genera el SQL (CREATE TABLE, FOREIGN KEY...) a partir de
estas clases con "makemigrations" y "migrate".

Diagrama de relaciones:

    Categoria (1) ──────< (N) Producto (N) >────── (1) Marca
                                                     (opcional)

  - Una Categoría tiene MUCHOS productos; un Producto pertenece a UNA categoría.
  - Una Marca tiene MUCHOS productos; un Producto puede tener UNA marca (o ninguna).
  - MensajeContacto es una tabla independiente (formulario de contacto).

En MySQL esto se traduce en las columnas productos_producto.categoria_id y
productos_producto.marca_id, cada una con su restricción FOREIGN KEY.
"""

from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    """
    Tabla productos_categoria: agrupa productos (Computación, Audio, etc.).

    Antes la categoría era un texto fijo (choices) dentro de Producto.
    Ahora es una tabla propia: el administrador puede crear categorías
    nuevas desde /admin/ sin modificar el código.
    """

    # unique=True: MySQL crea un índice UNIQUE y no permite dos categorías con el mismo nombre.
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre")
    # slug: versión "amigable para URL" del nombre (ej: "Periféricos" -> "perifericos").
    # Se usará para filtrar el catálogo por categoría (?categoria=perifericos).
    slug = models.SlugField(max_length=60, unique=True, blank=True, verbose_name="Slug (URL)")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']  # Orden alfabético por defecto en todas las consultas

    def __str__(self):
        # Es lo que se muestra al imprimir la categoría: {{ producto.categoria }} -> "Audio"
        return self.nombre

    def save(self, *args, **kwargs):
        # Si no se escribió un slug, se genera automáticamente desde el nombre antes de guardar.
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Marca(models.Model):
    """
    Tabla productos_marca: fabricante del producto (ASUS, Sony, Samsung...).
    """

    nombre = models.CharField(max_length=60, unique=True, verbose_name="Nombre")
    pais_origen = models.CharField(max_length=60, blank=True, verbose_name="País de origen")
    sitio_web = models.URLField(blank=True, verbose_name="Sitio web oficial")

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Tabla productos_producto: artículo a la venta en TechStore.
    Se relaciona con Categoria y Marca mediante claves foráneas (ForeignKey).
    """

    nombre = models.CharField(max_length=150, verbose_name="Nombre del Producto")

    # RELACIÓN 1: Producto -> Categoria (obligatoria).
    #   on_delete=PROTECT: MySQL/Django IMPIDEN borrar una categoría que todavía
    #     tiene productos (lanza ProtectedError). Así no quedan productos huérfanos.
    #   related_name='productos': permite la consulta inversa
    #     categoria.productos.all()  -> todos los productos de esa categoría.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name="Categoría",
    )

    # RELACIÓN 2: Producto -> Marca (opcional).
    #   null=True / blank=True: el producto puede no tener marca asignada.
    #   on_delete=SET_NULL: si se borra la marca, el producto NO se borra;
    #     solo queda con marca vacía (NULL).
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productos',
        verbose_name="Marca",
    )

    precio = models.PositiveIntegerField(verbose_name="Precio Normal (CLP)")
    descripcion = models.TextField(verbose_name="Descripción Detallada")
    imagen = models.URLField(max_length=500, verbose_name="URL de la Imagen")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock Disponible")
    oferta = models.BooleanField(default=False, verbose_name="¿En Oferta?")
    descuento = models.PositiveIntegerField(default=0, verbose_name="Porcentaje de Descuento (%)")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-id']

    def __str__(self):
        return f"{self.nombre} ({self.categoria})"

    # -----------------------------------------------------------------
    # PROPIEDADES CALCULADAS (@property)
    # No son columnas en MySQL: se calculan en Python cada vez que se leen.
    # En las plantillas se usan como un atributo más: {{ prod.precio_final_formateado }}
    # -----------------------------------------------------------------

    @property
    def precio_formateado(self):
        """Formato de moneda chilena con separador de miles ($1.299.990)."""
        return f"${self.precio:,.0f}".replace(",", ".")

    @property
    def ahorro(self):
        """Cálculo dinámico de ahorro en pesos según porcentaje de descuento."""
        if self.oferta and self.descuento > 0:
            return int(self.precio * (self.descuento / 100))
        return 0

    @property
    def ahorro_formateado(self):
        return f"${self.ahorro:,.0f}".replace(",", ".")

    @property
    def precio_final(self):
        """Precio descontado si el producto está en oferta."""
        if self.oferta and self.descuento > 0:
            return self.precio - self.ahorro
        return self.precio

    @property
    def precio_final_formateado(self):
        return f"${self.precio_final:,.0f}".replace(",", ".")

    @property
    def disponible(self):
        return self.stock > 0

    @property
    def mensaje_stock(self):
        if self.stock > 0:
            return f"¡En stock! ({self.stock} unidades disponibles)"
        return "Producto agotado temporalmente"


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    asunto = models.CharField(max_length=150, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje o Consulta")
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")
    leido = models.BooleanField(default=False, verbose_name="¿Atendido / Leído?")

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.asunto} - {self.nombre} ({self.email})"
