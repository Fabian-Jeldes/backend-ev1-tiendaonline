# TechStore Chile — Plataforma eCommerce en Django

> **Proyecto:** Programación Backend (`TI3V41 / FB50-N4-P13-C1`)  
> **Carrera:** Analista Programador / Ingeniería en Informática  
> **Institución:** INACAP — Sede Apoquindo  
> **Docente:** Claudio Rubilar Cid  
> **Framework:** Django 6.1 + Python 3.14 + Bootstrap 5  

---

## 📌 1. Descripción del Proyecto

**TechStore Chile** es una aplicación web eCommerce desarrollada con el framework Django. La solución promociona productos de tecnología, periféricos y hardware de alto rendimiento, estructurada bajo el patrón de arquitectura modular en dos aplicaciones desacopladas:
1. **`productos`**: Gestiona el catálogo, vista de detalle, filtrado de ofertas destacadas y lógica de negocio.
2. **`administracion`**: Provee un panel de control completo (CRUD) para que los administradores puedan crear, editar, modificar stock/precios y eliminar artículos sin requerir credenciales complejas.

Además, incorpora un **Carrito de Compras Lateral (Offcanvas Bootstrap 5)** que calcula subtotales y totales en moneda chilena (`$ CLP`), gestiona cantidades y **descuenta en tiempo real el stock visible en la tienda**, agotando los productos dinámicamente.

---

## 🎯 2. Módulos y Capacidades Técnicas del Sistema

| Módulo / Capacidad | Descripción Técnica | Archivos de Referencia |
| :--- | :--- | :--- |
| **Variables, Vistas y Enrutamiento** | Vistas basadas en funciones (`inicio`, `catalogo`, `detalle_producto`, `panel`, etc.), paso de diccionarios `contexto` vía `render()`, función de formato de moneda chilena `formato_clp()` y rutas dinámicas parametrizadas con `<int:id>/`. | `productos/views.py`<br>`administracion/views.py` |
| **Estructuras de Decisión y Colecciones** | Inventario estructurado en colecciones de diccionarios con persistencia JSON. Operadores relacionales (`==`, `>`), lógicos (`and`) y aritméticos (`*`, `/`, `-`) para cálculo dinámico de descuentos, ahorro y control de stock. | `productos/datos.py`<br>`productos/data/productos.json` |
| **Arquitectura Modular Desacoplada** | Separación de responsabilidades en aplicaciones independientes (`productos` y `administracion`) integradas limpiamente en el enrutador central mediante `include()`. | `tiendaonline/urls.py`<br>`tiendaonline/settings.py` |
| **Interfaz y Experiencia de Usuario (UI/UX)** | Framework Bootstrap 5 responsivo, identidad visual corporativa con logotipo SVG propio, estilos CSS personalizados, menú de 3 rutas y footer con información de soporte. | `templates/base.html`<br>`static/css/estilos.css` |

---

## 🗂️ 3. Estructura del Proyecto

```text
tiendaonline/
├── manage.py                          # Script de control y utilidades de Django
├── db.sqlite3                         # Base de datos local SQLite3
├── README.md                          # Documentación completa del proyecto
│
├── tiendaonline/                      # Configuración central del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                    # Configuración global (apps, templates, static)
│   ├── urls.py                        # Enrutador principal (include a cada app)
│   └── wsgi.py
│
├── productos/                         # Aplicación 1: Catálogo y Tienda
│   ├── data/
│   │   └── productos.json             # Persistencia de diccionarios de productos
│   ├── datos.py                       # Módulo de operaciones y funciones sobre diccionarios
│   ├── urls.py                        # Rutas de la app (/productos/, /productos/<id>/)
│   ├── views.py                       # Vistas de inicio, catálogo y detalle
│   └── ...
│
├── administracion/                    # Aplicación 2: Panel de Gestión CRUD
│   ├── urls.py                        # Rutas (/administracion/, /nuevo/, /editar/, /eliminar/)
│   ├── views.py                       # Lógica de creación, edición y borrado de productos
│   └── ...
│
├── templates/                         # Plantillas HTML con Django Template Language
│   ├── base.html                      # Layout maestro (Navbar 3 rutas, Drawer Carrito, Footer)
│   ├── index.html                     # Portada con banner y ofertas con descuento
│   ├── productos/
│   │   ├── catalogo.html              # Catálogo con stock reactivo y botón al carrito
│   │   └── detalle.html               # Detalle de producto con precio final y stock en vivo
│   └── administracion/
│       ├── panel.html                 # Tabla administrativa con métricas e inventario
│       └── formulario.html            # Formulario para agregar y editar productos
│
└── static/                            # Archivos estáticos del Frontend
    ├── css/
    │   └── estilos.css                # Estilos corporativos personalizados
    ├── img/
    │   └── logo.svg                   # Logotipo vectorial de TechStore
    └── js/
        └── carrito.js                 # Lógica reactiva del carrito y descuento de stock
```

---

## ⚙️ 4. Guía Maestra de Comandos de Django

### 4.1. Comandos de Creación e Inicialización

```powershell
# 1. Crear y activar un entorno virtual (opcional pero recomendado):
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instalar Django:
pip install django

# 3. Crear el proyecto Django en la carpeta actual:
django-admin startproject tiendaonline .

# 4. Crear aplicaciones modulares independientes:
py manage.py startapp productos
py manage.py startapp administracion
```

### 4.2. Comandos de Mantención y Base de Datos

```powershell
# 1. Verificar la integridad y sintaxis de todo el proyecto:
py manage.py check

# 2. Detectar cambios en modelos y generar archivos de migración:
py manage.py makemigrations

# 3. Aplicar migraciones a la base de datos (SQLite3):
py manage.py migrate

# 4. Ver el estado de las migraciones aplicadas:
py manage.py showmigrations

# 5. Crear un superusuario para el panel administrativo nativo de Django:
py manage.py createsuperuser

# 6. Abrir la consola interactiva de Django con el entorno cargado:
py manage.py shell
```

### 4.3. Comandos de Ejecución y Desarrollo Local

```powershell
# Iniciar el servidor local de desarrollo (por defecto en http://127.0.0.1:8000/):
py manage.py runserver

# Iniciar el servidor en un puerto alternativo (si el puerto 8000 está ocupado):
py manage.py runserver 8080

# Iniciar el servidor accesible desde otros dispositivos en la misma red local:
py manage.py runserver 0.0.0.0:8000
```
> *Para detener el servidor presiona `Ctrl + C` en la terminal.*

### 4.4. Comandos y Buenas Prácticas para Despliegue (Producción)

```powershell
# 1. Recopilar todos los archivos estáticos en una sola carpeta para producción:
py manage.py collectstatic

# 2. En settings.py para producción:
#    - DEBUG = False
#    - ALLOWED_HOSTS = ['tudominio.cl', 'www.tudominio.cl', '127.0.0.1']
#    - SECRET_KEY = os.environ.get('SECRET_KEY')  # Nunca en texto plano

# 3. En servidores Linux de producción (ej: Render, Railway, AWS, DigitalOcean):
#    pip install gunicorn
#    gunicorn tiendaonline.wsgi:application --bind 0.0.0.0:8000
```

---

## 🗺️ 5. Mapa de Rutas de la Aplicación

| URL | Método | App | Vista | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/` | `GET` | `productos` | `inicio` | Portada con Hero, ventajas y productos destacados en oferta. |
| `/productos/` | `GET` | `productos` | `catalogo` | Catálogo de productos con precios CLP y stock en vivo. |
| `/productos/<id>/` | `GET` | `productos` | `detalle_producto` | Ficha técnica con cálculo de descuento, ahorro y stock. |
| `/administracion/` | `GET` | `administracion` | `panel` | Tabla de gestión de inventario, métricas de stock y acciones. |
| `/administracion/nuevo/` | `GET / POST`| `administracion` | `nuevo_producto` | Formulario para registrar un nuevo artículo con foto. |
| `/administracion/editar/<id>/` | `GET / POST`| `administracion` | `editar_producto` | Modificación de título, precio, stock, oferta y descripción. |
| `/administracion/eliminar/<id>/`| `GET` | `administracion` | `eliminar_producto_view`| Baja de un artículo del inventario. |

---

## 🛒 6. Carrito de Compras Lateral y Descuento de Stock

* **Tecnología:** JavaScript Vanilla + Bootstrap 5 Offcanvas + `localStorage`.
* **Descuento de Stock en Vivo:** Al añadir un artículo al carrito, el script resta automáticamente la cantidad del stock visible en la tarjeta o página de detalle (`stock_disponible = stock_total - cantidad_en_carro`).
* **Regla de Negocio:** Si se añaden todas las unidades existentes al carro, el badge del producto se transforma a **Agotado** y el botón de compra se bloquea.
* **Formato de Moneda:** Subtotales y totales calculados dinámicamente con separador de miles en pesos chilenos (`$ CLP`).

---

## 🎓 7. Flujo de Demostración y Pruebas

Pasos recomendados para revisar y demostrar el funcionamiento completo del sistema:

1. **Iniciar el entorno local:**  
   `cd "c:\Users\fabia\Documents\_INACAP\Semestre 4\Backend\Ev1\tiendaonline"`  
   `py manage.py runserver`
2. **Modularización y Arquitectura:**  
   Revisar [tiendaonline/urls.py](tiendaonline/urls.py) y evidenciar la delegación de rutas mediante `include()` hacia las aplicaciones `productos` y `administracion`.
3. **Lógica de Negocio y Datos:**  
   Revisar [productos/datos.py](productos/datos.py) y [productos/views.py](productos/views.py), destacando la manipulación de diccionarios, cálculos de descuentos en tiempo de ejecución y validaciones condicionales.
4. **Carrito Lateral y Stock Dinámico:**  
   Desde el catálogo, agregar unidades del *Notebook ASUS* hasta agotar el stock disponible (5 unidades). Observar cómo la interfaz refleja el estado "Agotado" en tiempo real y cómo el panel lateral calcula el total en `$ CLP`.
5. **Panel Administrativo CRUD:**  
   Navegar a `/administracion/`, editar un producto (por ejemplo, reponer stock o modificar precios) y comprobar cómo se refleja instantáneamente en el catálogo y la portada.
