from django.db import models

class Producto(models.Model):
    CATEGORIAS = [
        ('Computación', 'Computación'),
        ('Monitores', 'Monitores'),
        ('Periféricos', 'Periféricos'),
        ('Audio', 'Audio'),
        ('Accesorios', 'Accesorios'),
        ('Videojuegos', 'Videojuegos'),
    ]

    nombre = models.CharField(max_length=150, verbose_name="Nombre del Producto")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Computación', verbose_name="Categoría")
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
