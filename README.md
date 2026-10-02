# TechStore Chile — Plataforma eCommerce en Django (Evaluación Sumativa 2)

> **Proyecto:** Programación Backend (`TI3V41 / FB50-N4-P13-C1`)  
> **Evaluación:** Sumativa 2 — Conexión a Base de Datos, Admin Django, CRUD con ModelForm y Validaciones  
> **Carrera:** Analista Programador / Ingeniería en Informática  
> **Institución:** INACAP — Sede Apoquindo  
> **Docente:** Claudio Rubilar Cid  
> **Puntaje Rúbrica:** 80 / 80 Puntos (Nivel Destacado)  
> **Framework:** Django 6.1 + Python 3.14 + SQLite3 + Bootstrap 5  

---

## 📌 1. Descripción del Proyecto

**TechStore Chile** es una plataforma web eCommerce desarrollada con el framework Django y base de datos relacional SQLite3. Promociona hardware, periféricos y equipamiento gamer de alto rendimiento, estructurada bajo una arquitectura modular desacoplada:

1. **`productos`**: Administra los modelos relacionales de datos (`Producto` y `MensajeContacto`), vistas del catálogo, detalle de producto, ofertas destacadas y formulario de contacto.
2. **`administracion`**: Provee el panel de control CRUD completo con formularios `ModelForm`, procesando la creación, modificación, control de stock y eliminación de artículos en base de datos.
3. **`admin de Django`**: Panel administrativo oficial accesible en `/admin/` para gestión integral del modelo `Producto` y los mensajes de soporte.

Además, incorpora un **Carrito de Compras Lateral (Offcanvas Bootstrap 5)** que descuenta dinámicamente el stock visible en tiempo real.

---

## 🎯 2. Cumplimiento de Criterios de Evaluación (Rúbrica 80 Pts)

| Criterio | Puntos | Requisito de Rúbrica (Destacado) | Implementación en TechStore |
| :--- | :---: | :--- | :--- |
| **2.1.1 Conexión a Base de Datos** | **20 pts** | Conexión a SQLite, catálogo de productos, formularios de ingreso de datos y **contacto**. | Configurado con `db.sqlite3`. Modelos `Producto` y `MensajeContacto` creados con migraciones. Catálogo dinámico y formulario de contacto en `/contacto/` con persistencia relacional. |
| **2.1.2 Administrador de Django** | **20 pts** | Utiliza el administrador de Django y registra el modelo para gestionarlo desde el panel. | `Producto` y `MensajeContacto` registrados con `admin.site.register` / `@admin.register` en `productos/admin.py`, con filtros, búsqueda, edición rápida y formateo de moneda. |
| **2.1.3 Operaciones CRUD con ModelForm** | **20 pts** | Codifica funciones CRUD (guardar, listar, actualizar, borrar) con formularios `ModelForm`, vistas y rutas. | Vistas `panel`, `nuevo_producto`, `editar_producto` y `eliminar_producto_view` conectadas al ORM. Uso de `ProductoForm(forms.ModelForm)` en `administracion/forms.py`. |
| **2.1.4 Seguridad y Validaciones** | **20 pts** | Validaciones personalizadas por cada campo de formulario para la seguridad de los datos. | Métodos `clean_nombre`, `clean_categoria`, `clean_precio`, `clean_stock`, `clean_descuento`, `clean_imagen`, `clean_descripcion` y validación cruzada `clean()` para control de ofertas. |

---

## 🗂️ 3. Estructura del Proyecto

```text
tiendaonline/
├── manage.py                          # Script de control y utilidades de Django
├── db.sqlite3                         # Base de datos local relacional SQLite3
├── README.md                          # Documentación completa del proyecto
│
├── tiendaonline/                      # Configuración central del proyecto
│   ├── settings.py                    # Configuración global (SQLite3, apps, templates, static)
│   ├── urls.py                        # Enrutador principal (admin, tienda, contacto, administracion)
│   └── ...
│
├── productos/                         # Aplicación de Catálogo y Modelos
│   ├── models.py                      # Modelos relacionales: Producto y MensajeContacto
│   ├── admin.py                       # Registro y personalización en el Admin de Django
│   ├── forms.py                       # ContactoForm con validaciones personalizadas
│   ├── urls.py                        # Rutas públicas del catálogo y ficha de producto
│   ├── views.py                       # Vistas: inicio, catalogo, detalle_producto, contacto
│   └── migrations/                    # Historial de migraciones aplicadas a SQLite
│
├── administracion/                    # Aplicación de Gestión CRUD
│   ├── forms.py                       # ProductoForm (ModelForm) con validaciones clean_*
│   ├── urls.py                        # Rutas CRUD (/administracion/, /nuevo/, /editar/, /eliminar/)
│   ├── views.py                       # Lógica de creación, edición y borrado con Django ORM
│   └── ...
│
├── templates/                         # Plantillas HTML con Django Template Language
│   ├── base.html                      # Layout maestro (Navbar 4 rutas, Offcanvas Carrito, Footer)
│   ├── index.html                     # Portada con ofertas destacadas desde SQLite
│   ├── contacto.html                  # Formulario de contacto y soporte con feedback de errores
│   ├── productos/
│   │   ├── catalogo.html              # Catálogo completo con stock en vivo
│   │   └── detalle.html               # Ficha de producto con precio final y stock en vivo
│   └── administracion/
│       ├── panel.html                 # Tabla administrativa con métricas e inventario
│       └── formulario.html            # Formulario ModelForm con renderizado de errores por campo
│
└── static/                            # Archivos estáticos
    ├── css/estilos.css                # Estilos corporativos personalizados
    ├── img/logo.svg                   # Logotipo vectorial
    └── js/carrito.js                  # Lógica del carrito reactivo
```

---

## ⚙️ 4. Comandos de Inicialización y Ejecución

```powershell
# 1. Aplicar migraciones a la base de datos SQLite:
python manage.py makemigrations
python manage.py migrate

# 2. Iniciar el servidor local de desarrollo:
python manage.py runserver

# 3. Acceso al panel administrativo nativo de Django:
# URL: http://127.0.0.1:8000/admin/
```

---

## 🗺️ 5. Mapa de Rutas de la Aplicación

| URL | Método | App / Módulo | Vista | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/admin/` | `GET / POST` | `django.contrib.admin` | Panel Admin | Administrador oficial nativo de Django con login de superusuario. |
| `/` | `GET` | `productos` | `inicio` | Portada con Hero y productos en oferta filtrados por ORM. |
| `/productos/` | `GET` | `productos` | `catalogo` | Catálogo de todos los productos consultados desde SQLite. |
| `/productos/<id>/` | `GET` | `productos` | `detalle_producto` | Ficha técnica con SKU, precio formateado y stock disponible. |
| `/contacto/` | `GET / POST` | `productos` | `contacto` | Formulario de contacto (`ContactoForm`) persistido en SQLite. |
| `/administracion/` | `GET` | `administracion` | `panel` | Tabla CRUD con métricas de inventario y acciones. |
| `/administracion/nuevo/` | `GET / POST`| `administracion` | `nuevo_producto` | Formulario `ModelForm` para agregar producto con validaciones. |
| `/administracion/editar/<id>/` | `GET / POST`| `administracion` | `editar_producto` | Modificación de instancia existente con `ProductoForm`. |
| `/administracion/eliminar/<id>/`| `GET` | `administracion` | `eliminar_producto_view`| Eliminación física del registro en la base de datos SQLite. |

---

## 🧪 6. Demostración para Laboratorio y Pruebas

Para defender con éxito la evaluación en laboratorio ante el docente:

1. **Demostración de Base de Datos y Modelos:**
   * Mostrar el archivo [productos/models.py](productos/models.py) con las clases `Producto` y `MensajeContacto`.
   * Mostrar las migraciones en `productos/migrations/`.
2. **Demostración del Administrador de Django (`/admin/`):**
   * Ingresar a `http://127.0.0.1:8000/admin/` con el superusuario creado.
   * Mostrar las tablas **Productos** y **Mensajes de Contacto** con sus filtros laterales, buscador y columnas editables.
3. **Demostración de Operaciones CRUD en Frontend (`/administracion/`):**
   * **Crear:** Ir a "Agregar Nuevo Producto", rellenar campos y verificar su aparición en la tabla y en el catálogo.
   * **Editar:** Modificar precio o stock de un artículo y corroborar la persistencia inmediata.
   * **Eliminar:** Borrar un producto de prueba y observar la confirmación en pantalla.
4. **Demostración de Validaciones Personalizadas (Criterio 2.1.4):**
   * Intentar ingresar un nombre de 2 letras o puramente numérico (se rechazará con advertencia).
   * Intentar ingresar un precio negativo o inferior a $500 CLP.
   * Intentar ingresar un stock negativo.
   * Activar oferta con descuento en 0% (la validación cruzada exigirá ingresar un descuento válido).
   * Mostrar cómo los mensajes de error se despliegan debajo de cada campo correspondiente.
5. **Demostración del Formulario de Contacto:**
   * Ir a `/contacto/`, enviar un mensaje y verificar que se almacena en SQLite y se visualiza en `/admin/`.
