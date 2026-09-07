import json
from pathlib import Path

RUTA_JSON = Path(__file__).resolve().parent / 'data' / 'productos.json'

def formato_clp(monto):
    """
    Función de formato monetario chileno (Criterio 1.1.1):
    Convierte un valor numérico a formato con punto de miles.
    Ejemplo: 1299990 -> '$1.299.990'
    """
    try:
        return f"${int(monto):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"


def obtener_productos():
    """
    Lee y retorna la lista de diccionarios de productos desde el archivo JSON (Criterio 1.1.2).
    Si no existe el archivo, retorna una lista vacía.
    """
    if not RUTA_JSON.exists():
        return []
    with open(RUTA_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_todos_los_productos(productos):
    """Guarda la lista de diccionarios en el archivo JSON."""
    RUTA_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_JSON, 'w', encoding='utf-8') as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)


def obtener_producto_por_id(id_producto):
    """Busca un producto por su ID en la colección de diccionarios."""
    productos = obtener_productos()
    for prod in productos:
        if prod['id'] == int(id_producto):
            return prod
    return None


def crear_producto(datos):
    """
    Crea un nuevo producto en la colección de diccionarios y lo persiste.
    """
    productos = obtener_productos()
    nuevo_id = max([p['id'] for p in productos], default=0) + 1
    
    nuevo_producto = {
        'id': nuevo_id,
        'nombre': datos.get('nombre', '').strip(),
        'categoria': datos.get('categoria', 'Tecnología').strip(),
        'precio': int(datos.get('precio', 0)),
        'descripcion': datos.get('descripcion', '').strip(),
        'imagen': datos.get('imagen', '').strip() or 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?auto=format&fit=crop&w=600&q=80',
        'stock': int(datos.get('stock', 0)),
        'oferta': bool(datos.get('oferta', False)),
        'descuento': int(datos.get('descuento', 0)),
    }
    
    productos.append(nuevo_producto)
    guardar_todos_los_productos(productos)
    return nuevo_producto


def actualizar_producto(id_producto, datos):
    """
    Actualiza los datos de un producto existente identificado por su ID.
    """
    productos = obtener_productos()
    actualizado = False
    
    for prod in productos:
        if prod['id'] == int(id_producto):
            prod['nombre'] = datos.get('nombre', prod['nombre']).strip()
            prod['categoria'] = datos.get('categoria', prod['categoria']).strip()
            prod['precio'] = int(datos.get('precio', prod['precio']))
            prod['descripcion'] = datos.get('descripcion', prod['descripcion']).strip()
            prod['imagen'] = datos.get('imagen', prod['imagen']).strip()
            prod['stock'] = int(datos.get('stock', prod['stock']))
            prod['oferta'] = bool(datos.get('oferta', prod['oferta']))
            prod['descuento'] = int(datos.get('descuento', prod['descuento']))
            actualizado = True
            break
            
    if actualizado:
        guardar_todos_los_productos(productos)
    return actualizado


def eliminar_producto(id_producto):
    """
    Elimina un producto por su ID de la colección de diccionarios.
    """
    productos = obtener_productos()
    productos_filtrados = [p for p in productos if p['id'] != int(id_producto)]
    if len(productos_filtrados) != len(productos):
        guardar_todos_los_productos(productos_filtrados)
        return True
    return False
