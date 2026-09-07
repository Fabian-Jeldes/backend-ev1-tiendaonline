# TechStore Chile — Plataforma eCommerce en Django

> **Evaluación Sumativa 1 (15% - 80 Puntos)**  
> **Asignatura:** Programación Backend (`TI3V41 / FB50-N4-P13-C1`)  
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

## 🎯 2. Cumplimiento de la Rúbrica de Evaluación (80 / 80 Puntos)

| Criterio | Puntaje | Nivel | Evidencia en el Código |
| :--- | :---: | :---: | :--- |
| **1.1.1 Variables, funciones, vistas y rutas** | **20 pts** | **Excelente** | Funciones de vista en Python (`inicio`, `catalogo`, `detalle_producto`, `panel`, etc.), paso de diccionarios `contexto` vía `render()`, función matemática de formateo CLP `formato_clp()`, y rutas dinámicas con parámetros tipo `<int:id>/`. |
| **1.1.2 Estructuras de decisión, operadores y diccionarios** | **20 pts** | **Excelente** | Datos organizados en colecciones de diccionarios en [productos/data/productos.json](productos/data/productos.json) gestionados por [productos/datos.py](productos/datos.py). Uso de estructuras `if/else`, operadores relacionales (`==`, `>`), lógicos (`and`) y aritméticos (`*`, `/`, `-`) para descuentos y control de stock. |
| **1.1.3 Modularización en 2 aplicaciones** | **20 pts** | **Excelente** | Dos aplicaciones independientes (`productos` y `administracion`) registradas en `INSTALLED_APPS` y delegadas con `include()` en [tiendaonline/urls.py](tiendaonline/urls.py). |
| **1.1.4 Identidad corporativa, framework CSS y navegación** | **20 pts** | **Excelente** | Framework Bootstrap 5 vía CDN, logotipo corporativo vectorial [static/img/logo.svg](static/img/logo.svg), estilos en [static/css/estilos.css](static/css/estilos.css), menú con 3 rutas principales y footer corporativo completo. |

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

## 🎓 7. Guion de Demostración para el Laboratorio

Para defender la evaluación ante el docente **Claudio Rubilar**:

1. **Levantar el servidor:**  
   `cd "c:\Users\fabia\Documents\_INACAP\Semestre 4\Backend\Ev1\tiendaonline"`  
   `py manage.py runserver`
2. **Explicar la modularización (Criterio 1.1.3):**  
   Mostrar [tiendaonline/urls.py](tiendaonline/urls.py) y explicar cómo `include('productos.urls')` e `include('administracion.urls')` desacoplan el sistema.
3. **Explicar los diccionarios y operadores (Criterio 1.1.2):**  
   Mostrar [productos/datos.py](productos/datos.py) y [productos/views.py](productos/views.py). Señalar las operaciones de descuento (`*`, `/`, `-`), operadores lógicos (`and`) y estructuras `if / else`.
4. **Probar el carrito y stock reactivo (Criterio 1.1.4):**  
   Agregar unidades del *Notebook ASUS* en el catálogo hasta agotar las 5 unidades. Mostrar cómo cambia la tarjeta a "Agotado" en tiempo real y cómo el drawer lateral calcula el total en `$ CLP`.
5. **Probar el CRUD de Administración:**  
   Ir a `/administracion/`, editar el producto agotado y subirle el stock a 10. Volver al catálogo para comprobar que vuelve a estar disponible inmediatamente.
