from django.contrib import admin
from .models import Producto, MensajeContacto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'categoria',
        'precio_formateado_display',
        'stock',
        'oferta',
        'descuento',
        'fecha_creacion'
    )
    list_display_links = ('id', 'nombre')
    list_filter = ('categoria', 'oferta', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('stock', 'oferta', 'descuento')
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
