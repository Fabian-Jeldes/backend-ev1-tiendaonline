# TechStore Chile — Backend Django + MySQL (Evaluación Sumativa 3)

> **Asignatura:** Programación Backend (`TI3041_FB50_N4_P13_C1`)  
> **Evaluación:** Sumativa 3 (30%): conexión a MySQL, CRUD con filtros, seguridad y uso de IA  
> **Carrera:** Analista Programador / Ingeniería en Informática  
> **Institución:** INACAP, Sede Apoquindo  
> **Docente:** Claudio Rubilar Cid  
> **Stack:** Django 6.1 · Python 3.14 · MySQL 8.4 (`mysqlclient`) · Bootstrap 5  
> **Bitácora de IA:** [BITACORA_IA.md](BITACORA_IA.md)

---

## 📌 1. Descripción del Proyecto

**TechStore Chile** es el backend de un eCommerce de tecnología. Guarda la información en una base de datos relacional externa **MySQL** y está organizado en tres apps:

1. **`productos`:** modelo relacional (`Categoria`, `Marca`, `Producto`, `MensajeContacto`), catálogo público con **búsqueda y filtros**, ficha de producto y formulario de contacto.
2. **`administracion`:** CRUD completo de productos con `ModelForm`, eliminación con confirmación y acceso protegido por **login y permisos**.
3. **`usuarios`:** inicio y cierre de sesión con `django.contrib.auth`, perfil del usuario y el grupo de permisos *Editores de catálogo*.

También usa el admin oficial de Django (`/admin/`) e incluye un carrito lateral (Offcanvas Bootstrap 5).

---

## 🎯 2. Cumplimiento de la Rúbrica (40 pts)

| Criterio | Indicador | Implementación | Dónde verlo |
| :--- | :--- | :--- | :--- |
| **2.1.1** Conexión a BD | Configuración MySQL | Conector `mysqlclient` y credenciales en `.env` (nunca en el código). Usuario propio sin root, `utf8mb4` y modo estricto. Migraciones aplicadas y verificadas en Workbench. | §4, [settings.py](tiendaonline/settings.py), [.env.example](.env.example) |
| **2.1.3** CRUD y filtrado | Modelo y operaciones CRUD | 3 clases relacionadas (`Categoria` 1─N `Producto` N─1 `Marca`) con `PROTECT` y `SET_NULL`, y una migración de datos reversible. CRUD completo. Filtros con `filter()`, `exclude()`, `Q` objects, `annotate(Case/When)` y `order_by()`. | §3.1, §3.2, §3.3, [filtros.py](productos/filtros.py) |
| **2.1.4** Seguridad | Protección de rutas críticas | `@login_required` + `@permission_required` en todas las vistas de administración. CSRF en todos los formularios. Borrado solo por POST y logout solo por POST. Roles con grupos. Sesión limitada a 2 horas. | §3.4, §3.5, [administracion/views.py](administracion/views.py) |
| **2.1.4** Uso de IA | Integración y uso crítico de IA | Bitácora con los prompts exactos, los problemas encontrados, las adaptaciones y cómo se validó cada una. 53 pruebas automáticas y una prueba de mutación. | [BITACORA_IA.md](BITACORA_IA.md), §5.1 |

---

## 🗂️ 3. Estructura del Proyecto

```text
tiendaonline/
├── manage.py                          # Script de control y utilidades de Django
├── requirements.txt                   # Dependencias (Django, mysqlclient, python-dotenv)
├── .env.example                       # Plantilla de variables de entorno (sin valores reales)
├── README.md                          # Documentación del proyecto
├── BITACORA_IA.md                     # Bitácora de uso de IA (prompts, adaptaciones, validación)
│
├── tiendaonline/
│   ├── settings.py                    # Configuración: MySQL vía .env, apps, seguridad de sesión
│   └── urls.py                        # Enrutador principal
│
├── productos/                         # Catálogo y modelo de datos
│   ├── models.py                      # Categoria, Marca, Producto (FK) y MensajeContacto
│   ├── filtros.py                     # FiltroProductosForm + consultas ORM de búsqueda/filtrado
│   ├── admin.py                       # Registro en el admin de Django
│   ├── views.py                       # inicio, catalogo (con filtros), detalle_producto, contacto
│   ├── tests.py                       # Pruebas de modelos y filtros
│   ├── fixtures/datos_iniciales.json  # 6 categorías, 8 marcas y 18 productos de demostración
│   └── migrations/                    # 0001 inicial · 0002-0004 migración a ForeignKey
│
├── administracion/                    # CRUD protegido
│   ├── forms.py                       # ProductoForm (ModelForm) con validaciones clean_*
│   ├── views.py                       # panel, nuevo, editar, eliminar (login + permisos)
│   └── tests.py                       # Pruebas de CRUD, control de acceso y CSRF
│
├── usuarios/                          # Autenticación
│   ├── forms.py                       # LoginForm (AuthenticationForm con estilo)
│   ├── views.py                       # IniciarSesionView, CerrarSesionView, perfil
│   ├── migrations/0001_grupo_editores.py  # Grupo "Editores de catálogo"
│   └── tests.py                       # Pruebas de login/logout
│
├── templates/
│   ├── base.html                      # Layout: navbar según sesión/permisos, carrito, footer
│   ├── 403.html                       # Página "Acceso denegado"
│   ├── productos/                     # catalogo.html, _filtros.html, detalle.html
│   ├── administracion/                # panel.html, formulario.html, confirmar_eliminar.html
│   └── usuarios/                      # login.html, perfil.html
│
└── static/                            # css/estilos.css · img/logo.svg · js/carrito.js
```

---

## 🧩 3.1 Modelo Relacional (Criterio 2.1.3)

El catálogo usa **tres tablas relacionadas** mediante claves foráneas, definidas en [productos/models.py](productos/models.py):

```text
 productos_categoria            productos_producto                  productos_marca
┌──────────────────┐          ┌──────────────────────────┐         ┌──────────────────┐
│ id (PK)          │ 1      N │ id (PK)                  │ N     1 │ id (PK)          │
│ nombre (UNIQUE)  │◄─────────┤ categoria_id (FK) NOT NULL│        │ nombre (UNIQUE)  │
│ slug (UNIQUE)    │          │ marca_id (FK) NULL       ├────────►│ pais_origen      │
│ descripcion      │          │ nombre, precio, stock,   │         │ sitio_web        │
└──────────────────┘          │ oferta, descuento, ...   │         └──────────────────┘
                              └──────────────────────────┘
```

| Relación | Tipo Django | `on_delete` | Efecto |
| :--- | :--- | :--- | :--- |
| Producto → Categoría | `ForeignKey` obligatoria | `PROTECT` | No se puede borrar una categoría que aún tiene productos (`ProtectedError`). |
| Producto → Marca | `ForeignKey` opcional (`null=True`) | `SET_NULL` | Al borrar una marca, sus productos quedan sin marca, pero no se borran. |

Ambas usan `related_name='productos'`, lo que permite la consulta inversa `categoria.productos.all()`.

**Migración de datos sin pérdida.** La categoría antes era un texto con `choices`. El cambio a `ForeignKey` se hizo en tres migraciones:

1. `0002_categoria_marca`: crea las tablas nuevas y una columna FK temporal.
2. `0003_poblar_categorias_marcas`: con `RunPython`, crea las categorías y marcas y enlaza cada producto existente. Es reversible.
3. `0004_producto_categoria_fk`: borra la columna de texto y deja la FK definitiva como `NOT NULL`.

## 🔎 3.2 Búsqueda y Filtrado con el ORM (Criterio 2.1.3)

El catálogo (`/productos/`) y el panel (`/administracion/`) comparten la misma barra de filtros. La lógica está en [productos/filtros.py](productos/filtros.py) y la plantilla en `templates/productos/_filtros.html`. Los filtros viajan por **GET** en la URL, así que una búsqueda se puede copiar o compartir. Antes de consultar MySQL, `FiltroProductosForm` valida cada valor.

| Filtro | Parámetro URL | Consulta ORM | SQL aproximado |
| :--- | :--- | :--- | :--- |
| Texto parcial | `?q=teclado inalámbrico` | `filter(Q(nombre__icontains=p) \| Q(descripcion__icontains=p) \| Q(marca__nombre__icontains=p) \| Q(categoria__nombre__icontains=p))` por cada palabra | `WHERE (nombre LIKE '%p%' OR ...) AND (...)` |
| Categoría (FK) | `?categoria=perifericos` | `filter(categoria=...)` | `WHERE categoria_id = 3` |
| Marca (FK) | `?marca=4` | `filter(marca=...)` | `WHERE marca_id = 4` |
| Rango de precio | `?precio_min=100000&precio_max=400000` | `annotate(precio_final_db=Case(When(...)))` + `filter(precio_final_db__gte=…, precio_final_db__lte=…)` | `CASE WHEN oferta ... END BETWEEN ...` |
| Disponibilidad | `?disponibles=on` | `exclude(stock=0)` | `WHERE NOT (stock = 0)` |
| Solo ofertas | `?ofertas=on` | `filter(oferta=True, descuento__gt=0)` | `WHERE oferta AND descuento > 0` |
| Orden | `?orden=precio_asc` | `order_by('precio_final_db')` | `ORDER BY precio_final_db ASC` |

Algunos detalles:
- **El rango de precio usa el precio final con descuento.** MySQL lo calcula con `annotate()`, porque la `@property` de Python no se puede usar en un `WHERE`.
- **Las búsquedas ignoran mayúsculas y tildes.** Gracias a la collation `utf8mb4_unicode_ci`, `inalambrico` también encuentra "Inalámbrico".
- **Los valores inválidos se descartan.** Si en la URL llega `precio_min=abc`, una categoría inexistente o un mínimo mayor que el máximo, ese filtro se ignora, se muestra el error y los demás filtros siguen funcionando.

---

## 🗑️ 3.3 Eliminación con Confirmación Previa (Criterios 2.1.3 y 2.1.4)

Antes, el botón de eliminar era un enlace GET con un `confirm()` de JavaScript: abrir la URL borraba el producto. Ahora el borrado se hace en **dos pasos**, controlados por el servidor ([administracion/views.py](administracion/views.py)):

| Paso | Petición | Qué hace |
| :--- | :--- | :--- |
| 1 | `GET /administracion/eliminar/5/` | Muestra `confirmar_eliminar.html` con los datos del producto. **No modifica la BD.** |
| 2 | `POST /administracion/eliminar/5/` + `csrfmiddlewaretoken` | Ejecuta `producto.delete()`, guarda un mensaje y redirige al panel (patrón *Post/Redirect/Get*). |

Por qué es más seguro:
- **Un GET nunca modifica datos.** Ni las precargas del navegador ni los enlaces que se abren solos pueden borrar productos.
- **Protección CSRF.** Una página externa no puede borrar con `<img src="/administracion/eliminar/5/">`, porque sin el token CSRF el POST recibe **403 Forbidden**.
- **`@require_http_methods(['GET', 'POST'])`.** Cualquier otro método HTTP recibe **405**.
- **Un id inexistente da 404.** Se usa `get_object_or_404`.

Se eligió el **borrado físico** (`DELETE FROM`). La rúbrica también acepta el borrado lógico, que consistiría en agregar un campo `activo` y marcarlo en `False` en lugar de borrar la fila.

---

## 🛡️ 3.4 Autenticación y Control de Acceso (Criterio 2.1.4)

Todas las vistas de administración/modificación exigen **sesión iniciada** y **el permiso de su acción**. Se usan dos decoradores en [administracion/views.py](administracion/views.py):

```python
@login_required                                                        # sin sesión  -> redirige a /usuarios/login/?next=...
@permission_required('productos.delete_producto', raise_exception=True)  # sin permiso -> 403 Prohibido
def eliminar_producto_view(request, id): ...
```

| Ruta | Permiso exigido | Anónimo | Usuario sin permisos | Grupo *Editores de catálogo* | Superusuario |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `/administracion/` | `view_producto` | 302 → login | 403 | ✅ 200 | ✅ 200 |
| `/administracion/nuevo/` | `add_producto` | 302 → login | 403 | ✅ 200 | ✅ 200 |
| `/administracion/editar/<id>/` | `change_producto` | 302 → login | 403 | ✅ 200 | ✅ 200 |
| `/administracion/eliminar/<id>/` | `delete_producto` | 302 → login | 403 | ❌ 403 | ✅ 200 |
| `/admin/` | `is_staff` | 302 → login | 302 → login | 302 → login | ✅ 200 |

La tabla se verificó con el cliente de pruebas de Django contra MySQL.

**Login y logout** ([usuarios/](usuarios/)). Se usan las vistas oficiales `LoginView` y `LogoutView` de `django.contrib.auth`, que ya incluyen:
- **Contraseñas con hash.** Se guardan con PBKDF2-SHA256, nunca en texto plano, y se exige que sean seguras (`AUTH_PASSWORD_VALIDATORS`).
- **Rotación de la sesión al iniciar sesión.** El id de sesión cambia al ingresar, lo que evita la *session fixation*.
- **Protección del parámetro `?next=`.** Después del login vuelve a la página que se quería abrir, pero bloquea las redirecciones a sitios externos (*open redirect*).
- **Mensaje de error genérico.** "Usuario o contraseña incorrectos" no revela si el usuario existe.
- **Logout solo por POST con CSRF.** Un sitio externo no puede cerrar tu sesión con un enlace.
- **Sesión limitada.** Expira a las 2 horas o al cerrar el navegador, y la cookie es `HttpOnly`, así que JavaScript no puede leerla.

**Roles.** La migración `usuarios/0001_grupo_editores` crea el grupo **Editores de catálogo**, que puede ver, crear y editar productos, pero no eliminarlos. Para asignarlo: `/admin/` → *Usuarios* → elegir el usuario → *Grupos*.

**Interfaz.** La barra de navegación muestra *Ingresar* o el menú del usuario (perfil, panel, cerrar sesión). El enlace *Admin Productos* solo aparece si se tiene permiso. Ocultar el enlace es solo comodidad: la protección real está en los decoradores. `/usuarios/perfil/` muestra los permisos del usuario conectado, y `templates/403.html` es la página de "Acceso denegado".

---

## 🔐 3.5 Manejo Seguro de Credenciales (Criterios 2.1.1 y 2.1.4)

Ninguna contraseña ni clave está escrita en el código fuente. El esquema es el siguiente:

| Archivo | ¿Se sube a git? | Contenido |
| :--- | :---: | :--- |
| `tiendaonline/settings.py` | ✅ Sí | Solo **nombres** de variables: `os.getenv('DB_PASSWORD')`. |
| `.env.example` | ✅ Sí | Plantilla con valores de ejemplo (`cambia-esta-contrasena`). |
| `.env` | ❌ No (`.gitignore`) | Valores **reales**. Existe solo en el equipo de cada desarrollador. |

**Buenas prácticas aplicadas:**
1. **Separar código y configuración.** Es el principio *12-Factor App*: el mismo código funciona en otro equipo cambiando solo el `.env`.
2. **Mínimo privilegio.** La app se conecta con `techstore_user`, que solo tiene permisos sobre `techstore_db`. La cuenta `root` no se usa nunca desde Django.
3. **Contraseñas fuertes y aleatorias.** Se generaron con el módulo `secrets` de Python (24 caracteres). La `SECRET_KEY` se generó con `get_random_secret_key()`.
4. **Fallar de forma segura.** Si falta una variable obligatoria, Django no arranca (`ImproperlyConfigured`). `DEBUG` es `False` por defecto y `ALLOWED_HOSTS` ya no acepta `'*'`.
5. **Acceso solo local.** MySQL escucha únicamente en `127.0.0.1`, así que no es accesible desde otros equipos de la red.
6. **Rotación.** La `SECRET_KEY` original (`django-insecure-...`) estaba escrita en `settings.py` y quedó en el historial público de GitHub. Se **reemplazó por una nueva**, así que la antigua ya no sirve para firmar sesiones.

**En producción** el `.env` se reemplaza por variables de entorno del servidor o por un gestor de secretos (Render/Railway *Environment*, GitHub Actions *Secrets*, AWS Secrets Manager, Azure Key Vault). `settings.py` no cambia, porque `os.getenv()` lee igual desde cualquiera de esas fuentes.

---

## ⚙️ 4. Configuración de la Base de Datos MySQL (Criterio 2.1.1)

El proyecto se conecta a un servidor **MySQL 8** externo mediante el conector oficial recomendado por Django, **`mysqlclient`**. Las credenciales **no están escritas en el código**: `settings.py` las lee desde un archivo `.env` (excluido de git) con `python-dotenv`. Si falta una variable obligatoria, Django se detiene con un mensaje `ImproperlyConfigured` que indica cuál.

### 4.1 Parámetros de conexión

| Variable (`.env`) | Parámetro en `DATABASES` | Valor por defecto | Descripción |
| :--- | :--- | :--- | :--- |
| — | `ENGINE` | `django.db.backends.mysql` | Backend MySQL de Django (usa `mysqlclient`). |
| `DB_NAME` | `NAME` | *(obligatoria)* | Nombre del esquema, p. ej. `techstore_db`. |
| `DB_USER` | `USER` | *(obligatoria)* | Usuario MySQL con permisos sobre el esquema. |
| `DB_PASSWORD` | `PASSWORD` | vacío | Contraseña del usuario. |
| `DB_HOST` | `HOST` | `127.0.0.1` | Host del servidor MySQL. |
| `DB_PORT` | `PORT` | `3306` | Puerto del servidor MySQL. |
| — | `OPTIONS.charset` | `utf8mb4` | Soporte completo de caracteres (tildes, ñ, emojis). |
| — | `OPTIONS.init_command` | `STRICT_TRANS_TABLES` | Modo estricto: rechaza datos inválidos en lugar de truncarlos. |

Además se leen `DJANGO_SECRET_KEY` (obligatoria), `DJANGO_DEBUG` y `DJANGO_ALLOWED_HOSTS`.

### 4.2 Crear el esquema y el usuario en MySQL

En MySQL Workbench (o `mysql -u root -p`):

```sql
CREATE DATABASE techstore_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'techstore_user'@'localhost' IDENTIFIED BY 'tu-contraseña-segura';
GRANT ALL PRIVILEGES ON techstore_db.* TO 'techstore_user'@'localhost';
-- Necesario solo para ejecutar los tests (Django crea la BD test_techstore_db):
GRANT ALL PRIVILEGES ON test_techstore_db.* TO 'techstore_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4.3 Instalación y ejecución

```powershell
# 1. Instalar dependencias:
pip install -r requirements.txt

# 2. Crear el archivo de entorno y completar las credenciales:
copy .env.example .env

# 3. Verificar la conexión y aplicar las migraciones en MySQL:
python manage.py check --database default
python manage.py migrate

# 4. Cargar los datos de demostración (6 categorías, 8 marcas y 18 productos):
python manage.py loaddata datos_iniciales

# 5. Crear superusuario e iniciar el servidor:
python manage.py createsuperuser
python manage.py runserver
```

### 4.4 Verificación en MySQL Workbench

En este equipo MySQL 8.4 corre como el servicio de Windows **`MySQL84`** (inicio automático, escuchando solo en `127.0.0.1:3306`). Para conectarse desde Workbench: *MySQL Connections → +*, host `127.0.0.1`, puerto `3306`, usuario `root` (contraseña en la variable `MYSQL_ROOT_PASSWORD` del `.env` local) o `techstore_user`.

Tras `migrate`, en el esquema `techstore_db` deben aparecer las tablas `productos_categoria`, `productos_marca`, `productos_producto`, `productos_mensajecontacto` y las de Django (`auth_user`, `django_session`, `django_migrations`, etc.). Consulta de comprobación:

```sql
USE techstore_db;
SHOW TABLES;
SELECT app, name, applied FROM django_migrations ORDER BY applied;
SELECT id, nombre, precio, stock FROM productos_producto;

-- Comprobar las relaciones (JOIN entre las 3 tablas):
SELECT p.nombre, c.nombre AS categoria, m.nombre AS marca
FROM productos_producto p
JOIN productos_categoria c ON c.id = p.categoria_id
LEFT JOIN productos_marca m ON m.id = p.marca_id;

-- Ver las claves foráneas creadas por Django:
SHOW CREATE TABLE productos_producto;
```

> En Workbench, *Database → Reverse Engineer* sobre `techstore_db` genera el diagrama ER con las relaciones. Es buena evidencia para la presentación.

---

## 🗺️ 5. Mapa de Rutas de la Aplicación

| URL | Método | App / Módulo | Vista | Descripción |
| :--- | :---: | :---: | :---: | :--- |
| `/admin/` | `GET / POST` | `django.contrib.admin` | Panel Admin | Administrador oficial nativo de Django con login de superusuario. |
| `/` | `GET` | `productos` | `inicio` | Portada con Hero y productos en oferta filtrados por ORM. |
| `/productos/` | `GET` | `productos` | `catalogo` | Catálogo con búsqueda y filtros por GET (`?q=`, `?categoria=`, `?precio_min=`, `?disponibles=`, `?ofertas=`, `?orden=`). |
| `/productos/<id>/` | `GET` | `productos` | `detalle_producto` | Ficha técnica con SKU, precio formateado y stock disponible. |
| `/contacto/` | `GET / POST` | `productos` | `contacto` | Formulario de contacto (`ContactoForm`) persistido en MySQL. |
| `/usuarios/login/` | `GET / POST` | `usuarios` | `IniciarSesionView` | Formulario de inicio de sesión (`LoginView`). Respeta `?next=`. |
| `/usuarios/logout/` | `POST` | `usuarios` | `CerrarSesionView` | Cierra la sesión (solo POST + CSRF; GET → 405). |
| `/usuarios/perfil/` | `GET` | `usuarios` | `perfil` | Datos y permisos del usuario conectado (`@login_required`). |
| `/administracion/` | `GET` | `administracion` | `panel` | Tabla CRUD con métricas de inventario y acciones. |
| `/administracion/nuevo/` | `GET / POST`| `administracion` | `nuevo_producto` | Formulario `ModelForm` para agregar producto con validaciones. |
| `/administracion/editar/<id>/` | `GET / POST`| `administracion` | `editar_producto` | Modificación de instancia existente con `ProductoForm`. |
| `/administracion/eliminar/<id>/`| `GET / POST` | `administracion` | `eliminar_producto_view`| **GET:** página de confirmación (no borra). **POST + CSRF:** eliminación física en MySQL. Otros métodos → 405. |

---

## ✅ 5.1 Pruebas Automáticas

El proyecto tiene **53 pruebas** (`django.test.TestCase`) que corren contra **MySQL**:

```powershell
python manage.py test            # todas las pruebas
python manage.py test usuarios   # solo una app
python manage.py test -v 2       # muestra el nombre de cada prueba
```

Django crea una base temporal `test_techstore_db`, aplica todas las migraciones (incluidas las de datos), ejecuta cada prueba dentro de una transacción que se deshace al terminar y luego borra la base temporal. Los datos reales de `techstore_db` no se tocan. Por eso, en la sección 4.2, el usuario de MySQL tiene permisos sobre `test_techstore_db`.

| Archivo | Pruebas | Qué verifica |
| :--- | :---: | :--- |
| [productos/tests.py](productos/tests.py) | 22 | Migración de datos, `slug` automático, `related_name`, `PROTECT`, `SET_NULL`, cálculo del precio final. Filtros por texto (varias palabras, sin tildes), categoría, rango de precio final, `exclude` de agotados, ofertas, orden, filtros combinados y rechazo de valores inválidos. |
| [administracion/tests.py](administracion/tests.py) | 20 | Matriz de acceso (anónimo → login, sin permisos → 403, editor sin *delete*, superusuario). CRUD completo, incluidos datos inválidos, id falso, 404 y 405. CSRF real con `Client(enforce_csrf_checks=True)`: un POST sin token recibe 403 y uno con token se acepta. |
| [usuarios/tests.py](usuarios/tests.py) | 11 | Hash PBKDF2 de la contraseña, login real con `next`, bloqueo de *open redirect*, error genérico, logout solo por POST, perfil protegido y barra de navegación según la sesión. |

**Prueba de que los tests detectan errores (mutación).** Se quitaron a propósito los decoradores `@login_required` y `@permission_required` de `eliminar_producto_view` y se ejecutó `python manage.py test administracion`: **fallaron 5 pruebas**, todas sobre la ruta de eliminar. Al restaurar el código volvieron a pasar las 20. Si alguien borra la protección por error, las pruebas lo avisan.

---

## 🧪 6. Guion de Demostración (Evaluación 3)

1. **MySQL (2.1.1).** Mostrar el `settings.py` comentado: solo tiene `os.getenv()`, no credenciales. Mostrar `.env.example` y explicar que `.env` está en `.gitignore`. En Workbench, `SHOW TABLES;`, el `JOIN` de la sección 4.4 y el diagrama ER (*Database → Reverse Engineer*).
2. **Modelo relacional (2.1.3).** En [models.py](productos/models.py), mostrar el diagrama de la cabecera y las dos `ForeignKey`. En `/admin/`, intentar borrar la categoría *Audio*: Django lo impide por `PROTECT`.
3. **Filtros (2.1.3).** En `/productos/`:
   - Buscar `inalambrico` (sin tilde): encuentra productos con "Inalámbrico".
   - Elegir la categoría *Audio* con un rango de $50.000 a $150.000.
   - Activar *Solo con stock*: desaparecen el teclado Razer y el parlante JBL, que están agotados.
   - Ordenar por precio.
   - Escribir `?precio_min=abc` en la URL para mostrar la validación.
4. **Seguridad (2.1.4).**
   - Sin sesión, abrir `/administracion/`: redirige al login.
   - Entrar con un usuario del grupo *Editores de catálogo*: puede crear y editar, pero eliminar da **403**.
   - Entrar como superusuario y eliminar un producto: primero aparece la confirmación (GET) y el borrado ocurre recién con el POST.
   - Mostrar `{% csrf_token %}` en el código fuente de la página.
5. **CRUD completo (2.1.3).** Crear un producto y probar las validaciones: nombre de 2 letras, precio menor a $500, oferta con 0% de descuento. Luego editarlo y eliminarlo.
6. **Pruebas.** Ejecutar `python manage.py test` en vivo: `Ran 53 tests ... OK`.
7. **IA (2.1.4).** Presentar [BITACORA_IA.md](BITACORA_IA.md) y las diapositivas: los prompts exactos, los problemas reales (MySQL no instalado, fotos que no calzaban, logout por GET) y cómo se validó cada uno.
