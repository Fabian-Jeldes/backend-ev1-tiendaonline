"""
=====================================================================
 productos/admin.py — Registro de modelos en el panel /admin/ de Django
=====================================================================

Cada clase "XxxAdmin" define cómo se ve una tabla en el administrador:
columnas visibles, filtros laterales, buscador y campos editables.
"""

from django.contrib import admin
from django.db.models import Count

from .models import Categoria, Marca, MensajeContacto, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'slug', 'total_productos')
    search_fields = ('nombre',)
    # El slug se rellena solo mientras se escribe el nombre (JavaScript del admin).
    prepopulated_fields = {'slug': ('nombre',)}

    def get_queryset(self, request):
        # annotate + Count: MySQL calcula cuántos productos tiene cada categoría
        # en UNA sola consulta (GROUP BY), en vez de una consulta por fila.
        return super().get_queryset(request).annotate(num_productos=Count('productos'))

    @admin.display(description="N° de productos", ordering='num_productos')
    def total_productos(self, obj):
        return obj.num_productos


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'pais_origen', 'sitio_web', 'total_productos')
    search_fields = ('nombre', 'pais_origen')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_productos=Count('productos'))

    @admin.display(description="N° de productos", ordering='num_productos')
    def total_productos(self, obj):
        return obj.num_productos


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'categoria',
        'marca',
        'precio_formateado_display',
        'stock',
        'oferta',
        'descuento',
        'fecha_creacion'
    )
    list_display_links = ('id', 'nombre')
    # Filtros laterales: ahora categoría y marca se filtran por relación (FK).
    list_filter = ('categoria', 'marca', 'oferta', 'fecha_creacion')
    # "categoria__nombre" busca a través de la relación (JOIN con productos_categoria).
    search_fields = ('nombre', 'descripcion', 'categoria__nombre', 'marca__nombre')
    list_editable = ('stock', 'oferta', 'descuento')
    # select_related: trae categoría y marca en la MISMA consulta (JOIN),
    # evitando el problema "N+1" (una consulta extra por cada producto).
    list_select_related = ('categoria', 'marca')
    list_per_page = 15

    @admin.display(description="Precio Normal (CLP)")
    def precio_formateado_display(self, obj):
        return obj.precio_formateado


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'asunto', 'fecha_envio', 'leido')
    list_display_links = ('id', 'nombre', 'asunto')
    list_filter = ('leido', 'fecha_envio')
    search_fields = ('nombre', 'email', 'asunto', 'mensaje')
    list_editable = ('leido',)
    list_per_page = 20
    readonly_fields = ('fecha_envio',)
