from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Producto
from .forms import ContactoForm
from .filtros import FiltroProductosForm, aplicar_filtros

def inicio(request):
    """
    Vista para la página principal (index.html).
    Obtiene los productos en oferta directamente desde MySQL mediante el ORM de Django.
    """
    # select_related('categoria', 'marca'): un solo SELECT con JOIN a las tablas
    # relacionadas, en vez de una consulta extra por cada producto mostrado.
    destacados = Producto.objects.filter(oferta=True).select_related('categoria', 'marca')
    contexto = {
        'titulo': 'Bienvenido a TechStore Chile',
        'destacados': destacados,
    }
    return render(request, 'index.html', contexto)


def catalogo(request):
    """
    READ & FILTER del CRUD (Criterio 2.1.3): listado de productos con filtros.

    Flujo:
      1. Los filtros llegan por GET en la URL (ej: /productos/?q=sony&ofertas=on).
         Se usa GET y no POST porque buscar no modifica datos, y así la URL
         filtrada se puede copiar, compartir o guardar en favoritos.
      2. FiltroProductosForm valida los parámetros.
      3. aplicar_filtros() arma la consulta ORM con los valores válidos.
    """
    # request.GET or None: si la URL no trae parámetros, el formulario queda "sin enviar"
    # y no muestra errores; solo se listan todos los productos.
    form = FiltroProductosForm(request.GET or None)
    datos = form.datos_validos()

    todos = Producto.objects.select_related('categoria', 'marca')
    productos = aplicar_filtros(todos, datos)

    contexto = {
        'titulo_seccion': 'Catálogo de Productos',
        'form': form,
        'productos': productos,
        'total_productos': todos.count(),          # SELECT COUNT(*) sin filtros
        'total_filtrados': productos.count(),      # SELECT COUNT(*) con los filtros aplicados
        'hay_filtros': form.hay_filtros(),
    }
    return render(request, 'productos/catalogo.html', contexto)


def detalle_producto(request, id):
    """
    Vista que busca un producto por su clave primaria (ID) en la base de datos.
    Aprovecha las propiedades del modelo Producto para los cálculos dinámicos de oferta y stock.
    """
    producto = get_object_or_404(Producto.objects.select_related('categoria', 'marca'), pk=id)
    tiene_descuento = producto.oferta and producto.descuento > 0

    contexto = {
        'producto': producto,
        'precio_original_formateado': producto.precio_formateado,
        'precio_final_formateado': producto.precio_final_formateado,
        'monto_ahorro_formateado': producto.ahorro_formateado,
        'tiene_descuento': tiene_descuento,
        'disponible': producto.disponible,
        'mensaje_stock': producto.mensaje_stock,
    }
    return render(request, 'productos/detalle.html', contexto)


def contacto(request):
    """
    Vista para el Formulario de Contacto (Criterio 2.1.1).
    Procesa el formulario ModelForm con validaciones personalizadas y persiste en MySQL.
    """
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            mensaje = form.save()
            messages.success(
                request,
                f"¡Gracias {mensaje.nombre}! Tu consulta #{mensaje.id} ha sido registrada exitosamente. Nuestro equipo se contactará contigo."
            )
            return redirect('contacto')
        else:
            messages.error(request, "Por favor corrige los errores señalados en el formulario de contacto.")
    else:
        form = ContactoForm()

    contexto = {
        'titulo': 'Contacto & Soporte Técnico',
        'form': form,
    }
    return render(request, 'contacto.html', contexto)
