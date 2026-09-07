from django.shortcuts import render, redirect, Http404
from django.contrib import messages
from productos.datos import (
    obtener_productos,
    obtener_producto_por_id,
    crear_producto,
    actualizar_producto,
    eliminar_producto,
    formato_clp,
)

def panel(request):
    """
    Vista principal del Panel de Administración (READ del CRUD).
    Lista todos los productos, su stock, precios y estado.
    """
    productos = obtener_productos()
    
    # Añadimos formato CLP para visualización en la tabla
    for p in productos:
        p['precio_formateado'] = formato_clp(p['precio'])

    # Estadísticas para el resumen administrativo
    total_productos = len(productos)
    agotados = len([p for p in productos if p['stock'] <= 0])
    en_oferta = len([p for p in productos if p['oferta']])

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
    Gestiona el método GET para mostrar el formulario y POST para persistir los datos.
    """
    if request.method == 'POST':
        datos = {
            'nombre': request.POST.get('nombre', '').strip(),
            'categoria': request.POST.get('categoria', 'Tecnología').strip(),
            'precio': request.POST.get('precio', 0),
            'descripcion': request.POST.get('descripcion', '').strip(),
            'imagen': request.POST.get('imagen', '').strip(),
            'stock': request.POST.get('stock', 0),
            'oferta': 'oferta' in request.POST,
            'descuento': request.POST.get('descuento', 0) if 'oferta' in request.POST else 0,
        }
        
        # Validamos que al menos tenga nombre y precio
        if datos['nombre'] and int(datos['precio']) >= 0:
            nuevo = crear_producto(datos)
            messages.success(request, f"¡Producto '{nuevo['nombre']}' agregado con éxito!")
            return redirect('admin_panel')
        else:
            messages.error(request, "Por favor completa todos los campos requeridos con valores válidos.")

    contexto = {
        'titulo': 'Agregar Nuevo Producto',
        'accion': 'Crear',
        'producto': None,
    }
    return render(request, 'administracion/formulario.html', contexto)


def editar_producto(request, id):
    """
    Vista para modificar un producto existente (UPDATE del CRUD).
    Carga los datos actuales en el formulario y guarda los cambios vía POST.
    """
    producto = obtener_producto_por_id(id)
    if not producto:
        raise Http404(f"El producto con ID {id} no existe.")

    if request.method == 'POST':
        datos = {
            'nombre': request.POST.get('nombre', '').strip(),
            'categoria': request.POST.get('categoria', '').strip(),
            'precio': request.POST.get('precio', 0),
            'descripcion': request.POST.get('descripcion', '').strip(),
            'imagen': request.POST.get('imagen', '').strip(),
            'stock': request.POST.get('stock', 0),
            'oferta': 'oferta' in request.POST,
            'descuento': request.POST.get('descuento', 0) if 'oferta' in request.POST else 0,
        }
        
        if datos['nombre']:
            actualizar_producto(id, datos)
            messages.success(request, f"¡Producto '{datos['nombre']}' actualizado correctamente!")
            return redirect('admin_panel')
        else:
            messages.error(request, "El nombre del producto no puede quedar vacío.")

    contexto = {
        'titulo': f"Editar Producto: {producto['nombre']}",
        'accion': 'Guardar Cambios',
        'producto': producto,
    }
    return render(request, 'administracion/formulario.html', contexto)


def eliminar_producto_view(request, id):
    """
    Vista para eliminar un producto (DELETE del CRUD).
    """
    producto = obtener_producto_por_id(id)
    if producto:
        nombre = producto['nombre']
        eliminar_producto(id)
        messages.success(request, f"El producto '{nombre}' ha sido eliminado.")
    else:
        messages.error(request, "El producto que intentas eliminar no fue encontrado.")
        
    return redirect('admin_panel')
