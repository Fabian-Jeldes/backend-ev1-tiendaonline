from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from productos.models import Producto
from .forms import ProductoForm

def panel(request):
    """
    Vista principal del Panel de Administración (READ del CRUD).
    Lista todos los productos desde la base de datos SQLite con sus métricas.
    """
    productos = Producto.objects.all()

    # Métricas calculadas con consultas del ORM de Django
    total_productos = productos.count()
    agotados = productos.filter(stock__lte=0).count()
    en_oferta = productos.filter(oferta=True).count()

    contexto = {
        'titulo': 'Panel de Administración de Productos',
        'productos': productos,
        'total_productos': total_productos,
        'agotados': agotados,
        'en_oferta': en_oferta,
    }
    return render(request, 'administracion/panel.html', contexto)


def nuevo_producto(request):
    """
    Vista para crear un nuevo producto (CREATE del CRUD).
    Utiliza ProductoForm (ModelForm) con validaciones personalizadas.
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"¡Producto '{producto.nombre}' agregado con éxito a la base de datos!")
            return redirect('admin_panel')
        else:
            messages.error(request, "Por favor corrige los errores señalados en el formulario.")
    else:
        form = ProductoForm()

    contexto = {
        'titulo': 'Agregar Nuevo Producto',
        'accion': 'Crear Producto',
        'form': form,
        'producto': None,
    }
    return render(request, 'administracion/formulario.html', contexto)


def editar_producto(request, id):
    """
    Vista para modificar un producto existente (UPDATE del CRUD).
    Carga la instancia actual en el ModelForm y persiste los cambios.
    """
    producto = get_object_or_404(Producto, pk=id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"¡Producto '{producto.nombre}' actualizado correctamente en la base de datos!")
            return redirect('admin_panel')
        else:
            messages.error(request, "Por favor corrige los errores señalados en el formulario.")
    else:
        form = ProductoForm(instance=producto)

    contexto = {
        'titulo': f"Editar Producto: {producto.nombre}",
        'accion': 'Guardar Cambios',
        'form': form,
        'producto': producto,
    }
    return render(request, 'administracion/formulario.html', contexto)


def eliminar_producto_view(request, id):
    """
    Vista para eliminar un producto de la base de datos (DELETE del CRUD).
    """
    producto = get_object_or_404(Producto, pk=id)
    nombre = producto.nombre
    producto.delete()
    messages.success(request, f"El producto '{nombre}' ha sido eliminado de la base de datos.")
    return redirect('admin_panel')
