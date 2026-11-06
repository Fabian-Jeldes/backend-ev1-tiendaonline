"""
=====================================================================
 administracion/views.py — CRUD de productos (Criterios 2.1.3 y 2.1.4)
=====================================================================

SEGURIDAD: todas las vistas de este archivo están protegidas con DOS
decoradores, que se aplican de arriba hacia abajo:

  @login_required
      Si NO hay sesión iniciada, redirige a /usuarios/login/?next=<ruta>.

  @permission_required('productos.<accion>_producto', raise_exception=True)
      Si HAY sesión pero el usuario no tiene ese permiso, responde
      403 Prohibido (plantilla templates/403.html) en vez de mostrar la página.

Django crea 4 permisos por cada modelo (view, add, change, delete) en la tabla
auth_permission. Cada vista exige el permiso que corresponde a su acción:

  panel                  -> productos.view_producto    (Read)
  nuevo_producto         -> productos.add_producto     (Create)
  editar_producto        -> productos.change_producto  (Update)
  eliminar_producto_view -> productos.delete_producto  (Delete)

Un superusuario tiene todos los permisos. El grupo "Editores de catálogo"
(migración usuarios/0001) puede ver, crear y editar, pero NO eliminar.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from productos.models import Producto
from productos.filtros import FiltroProductosForm, aplicar_filtros
from .forms import ProductoForm

@login_required
@permission_required('productos.view_producto', raise_exception=True)
def panel(request):
    """
    Vista principal del Panel de Administración (READ del CRUD).
    Lista los productos desde MySQL con sus métricas y filtros.
    """
    # select_related: trae categoría y marca con un JOIN (evita N+1 consultas).
    todos = Producto.objects.select_related('categoria', 'marca')

    # Métricas calculadas con consultas del ORM de Django (sobre TODO el inventario).
    total_productos = todos.count()
    agotados = todos.filter(stock__lte=0).count()
    en_oferta = todos.filter(oferta=True).count()

    # Mismos filtros que el catálogo público (productos/filtros.py), reutilizados aquí
    # para que el administrador encuentre rápido un producto en la tabla.
    form = FiltroProductosForm(request.GET or None)
    productos = aplicar_filtros(todos, form.datos_validos())

    contexto = {
        'titulo': 'Panel de Administración de Productos',
        'form': form,
        'hay_filtros': form.hay_filtros(),
        'total_filtrados': productos.count(),
        'productos': productos,
        'total_productos': total_productos,
        'agotados': agotados,
        'en_oferta': en_oferta,
    }
    return render(request, 'administracion/panel.html', contexto)


@login_required
@permission_required('productos.add_producto', raise_exception=True)
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


@login_required
@permission_required('productos.change_producto', raise_exception=True)
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


@login_required
@permission_required('productos.delete_producto', raise_exception=True)
@require_http_methods(['GET', 'POST'])
def eliminar_producto_view(request, id):
    """
    DELETE del CRUD con confirmación previa (Criterio 2.1.3 y 2.1.4).

    Funciona en dos pasos:
      1. GET  /administracion/eliminar/<id>/  -> NO borra nada. Solo muestra una
         página de confirmación con los datos del producto.
      2. POST /administracion/eliminar/<id>/  -> borra el producto (DELETE en MySQL)
         y redirige al panel.

    ¿Por qué no borrar directamente con un enlace (GET), como antes?
      - Un GET debe ser "seguro": solo leer, nunca modificar datos. Los navegadores,
        buscadores y antivirus pueden abrir enlaces solos (precarga), y eso habría
        borrado productos sin que nadie hiciera clic.
      - Ataque CSRF: otra página podría incluir <img src=".../eliminar/5/"> y el
        navegador del administrador lo abriría con su sesión, borrando el producto.
        Con POST, Django exige el {% csrf_token %} del formulario; una página ajena
        no puede conocer ese token, así que la petición es rechazada (error 403).
      - El confirm() de JavaScript se podía saltar (JS desactivado o URL abierta
        directamente). La confirmación ahora la controla el servidor.

    @require_http_methods: cualquier otro método (PUT, DELETE...) responde 405.
    """
    producto = get_object_or_404(Producto.objects.select_related('categoria', 'marca'), pk=id)

    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()  # Borrado físico: DELETE FROM productos_producto WHERE id = ...
        messages.success(request, f"El producto '{nombre}' ha sido eliminado de la base de datos.")
        # Patrón Post/Redirect/Get: tras un POST se redirige, así recargar la página
        # (F5) no reenvía el formulario por segunda vez.
        return redirect('admin_panel')

    # GET: mostrar la página de confirmación.
    contexto = {
        'titulo': f"Eliminar Producto: {producto.nombre}",
        'producto': producto,
    }
    return render(request, 'administracion/confirmar_eliminar.html', contexto)
