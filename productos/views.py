from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Producto
from .forms import ContactoForm

def inicio(request):
    """
    Vista para la página principal (index.html).
    Obtiene los productos en oferta directamente desde SQLite mediante el ORM de Django.
    """
    destacados = Producto.objects.filter(oferta=True)
    contexto = {
        'titulo': 'Bienvenido a TechStore Chile',
        'destacados': destacados,
    }
    return render(request, 'index.html', contexto)


def catalogo(request):
    """
    Vista que muestra el catálogo completo de productos consultando la base de datos SQLite.
    """
    productos = Producto.objects.all()
    contexto = {
        'titulo_seccion': 'Catálogo de Productos',
        'productos': productos,
        'total_productos': productos.count(),
    }
    return render(request, 'productos/catalogo.html', contexto)


def detalle_producto(request, id):
    """
    Vista que busca un producto por su clave primaria (ID) en la base de datos.
    Aprovecha las propiedades del modelo Producto para los cálculos dinámicos de oferta y stock.
    """
    producto = get_object_or_404(Producto, pk=id)
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
    Procesa el formulario ModelForm con validaciones personalizadas y persiste en SQLite.
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
