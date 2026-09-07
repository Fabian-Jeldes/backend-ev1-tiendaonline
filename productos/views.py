from django.shortcuts import render, Http404
from .datos import obtener_productos, obtener_producto_por_id, formato_clp

def inicio(request):
    """
    Vista para la página principal (index.html).
    Filtra y envía los productos que están en oferta a la portada con sus precios formateados en CLP.
    """
    productos = obtener_productos()
    
    # Preparamos los datos con formato monetario y cálculo de ofertas
    for p in productos:
        p['precio_formateado'] = formato_clp(p['precio'])
        if p['oferta'] and p['descuento'] > 0:
            ahorro = int(p['precio'] * (p['descuento'] / 100))
            p['precio_final'] = p['precio'] - ahorro
            p['precio_final_formateado'] = formato_clp(p['precio_final'])
        else:
            p['precio_final'] = p['precio']
            p['precio_final_formateado'] = p['precio_formateado']

    productos_destacados = [p for p in productos if p['oferta']]
    contexto = {
        'titulo': 'Bienvenido a TechStore Chile',
        'destacados': productos_destacados,
    }
    return render(request, 'index.html', contexto)


def catalogo(request):
    """
    Vista que muestra el catálogo completo de productos.
    Pasa la colección de diccionarios al contexto de la plantilla con precios en formato CLP.
    """
    productos = obtener_productos()
    
    for p in productos:
        p['precio_formateado'] = formato_clp(p['precio'])
        if p['oferta'] and p['descuento'] > 0:
            ahorro = int(p['precio'] * (p['descuento'] / 100))
            p['precio_final'] = p['precio'] - ahorro
            p['precio_final_formateado'] = formato_clp(p['precio_final'])
        else:
            p['precio_final'] = p['precio']
            p['precio_final_formateado'] = p['precio_formateado']

    contexto = {
        'titulo_seccion': 'Catálogo de Productos',
        'productos': productos,
        'total_productos': len(productos),
    }
    return render(request, 'productos/catalogo.html', contexto)


def detalle_producto(request, id):
    """
    Vista que busca un producto por su ID y calcula datos dinámicos
    utilizando estructuras de decisión (if/else) y operadores (Criterio 1.1.2).
    """
    producto_encontrado = obtener_producto_por_id(id)

    # Estructura de decisión: si no existe el producto, lanzamos error 404
    if producto_encontrado is None:
        raise Http404(f"El producto con ID {id} no fue encontrado en nuestro catálogo.")

    # Estructuras de decisión y operadores lógicos/aritméticos para cálculos de negocio
    precio_original = producto_encontrado['precio']
    precio_final = precio_original
    monto_ahorro = 0
    tiene_descuento = False

    # Operadores: 'and', '>', '-' y '*'
    if producto_encontrado['oferta'] and producto_encontrado['descuento'] > 0:
        tiene_descuento = True
        monto_ahorro = int(precio_original * (producto_encontrado['descuento'] / 100))
        precio_final = precio_original - monto_ahorro

    # Verificación de disponibilidad de stock con operadores relacionales
    if producto_encontrado['stock'] > 0:
        disponible = True
        mensaje_stock = f"¡En stock! ({producto_encontrado['stock']} unidades disponibles)"
    else:
        disponible = False
        mensaje_stock = "Producto agotado temporalmente"

    # Construcción del diccionario de contexto que viaja a la plantilla HTML con formato CLP
    contexto = {
        'producto': producto_encontrado,
        'precio_original_formateado': formato_clp(precio_original),
        'precio_final_formateado': formato_clp(precio_final),
        'monto_ahorro_formateado': formato_clp(monto_ahorro),
        'tiene_descuento': tiene_descuento,
        'disponible': disponible,
        'mensaje_stock': mensaje_stock,
    }
    return render(request, 'productos/detalle.html', contexto)
