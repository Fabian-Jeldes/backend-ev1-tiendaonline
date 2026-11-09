# Bitácora de Uso de Inteligencia Artificial — Evaluación 3

> **Proyecto:** TechStore Chile (Django + MySQL)  
> **Asignatura:** Programación Backend (`TI3041_FB50_N4_P13_C1`) · INACAP Apoquindo  
> **Docente:** Claudio Rubilar Cid  
> **Criterio evaluado:** 2.1.4 — *Orientaciones generadas por herramientas de inteligencia artificial*

---

## 1. Metodología de Trabajo

En lugar de pedirle a la IA que hiciera todo el proyecto de una sola vez, trabajé por etapas para entender cada cambio y probar que nada se rompiera en el camino:

1. **Revisión de lo que faltaba:** Primero le pasé la pauta de la Evaluación 3 para comparar lo que ya tenía de la entrega anterior (que estaba en SQLite y sin login) contra lo que pedía el profesor ahora.
2. **Avance paso a paso:** Dividimos el trabajo por temas: primero la conexión a MySQL, después el modelo relacional, luego los filtros del catálogo, la seguridad del CRUD con sesiones y, al final, las pruebas.
3. **Pruebas y correcciones:** Después de cada cambio revisé el proyecto en el navegador, comprobé las tablas en MySQL Workbench y corrí `manage.py check` y `manage.py test`.

---

## 2. Prompts Utilizados

Estos fueron los prompts principales que fui usando durante el desarrollo:

| Etapa | Prompt utilizado | Qué buscaba resolver |
| :---: | :--- | :--- |
| **1. Diagnóstico** | *"Hola, te adjunto la pauta de la Evaluación 3. ¿Qué cosas le faltan a mi proyecto actual para cumplir con todos los puntos de la rúbrica y en qué orden me conviene ir haciéndolas?"* | Identificar las brechas entre la entrega 2 y la entrega 3 antes de tocar el código. |
| **2. Conexión a MySQL** | *"Necesito pasar la base de datos de SQLite a MySQL usando mysqlclient. Además quiero sacar la SECRET_KEY y las contraseñas del settings.py para leerlas desde un archivo .env, dejando un .env.example para subir a GitHub."* | Cumplir el criterio **2.1.1** (conexión a MySQL y manejo seguro de credenciales sin hardcodearlas). |
| **3. Modelo Relacional** | *"Ahora la categoría es solo un texto fijo dentro de Producto. Ayúdame a crear los modelos Categoria y Marca como tablas separadas y conectarlas con ForeignKey a Producto, pero sin perder los productos que ya tengo creados."* | Cumplir el criterio **2.1.3** pasando de una sola tabla a un modelo relacional con `PROTECT` y `SET_NULL`. |
| **4. Buscador y Filtros** | *"En el catálogo necesito agregar una barra de filtros por GET: buscador por texto (nombre, descripción o marca), filtro por categoría, rango de precio mínimo y máximo, y checkboxes para ver solo con stock o solo ofertas."* | Implementar consultas avanzadas con el ORM de Django (`filter`, `exclude`, `Q` objects y `order_by`). |
| **5. Borrado en 2 pasos** | *"Actualmente el botón de eliminar borra el producto directo con un enlace GET y un alert de JavaScript. ¿Cómo lo cambio a una página de confirmación previa que solo borre cuando se envíe por POST con token CSRF?"* | Evitar borrados accidentales o por URL directa, exigiendo confirmación y protección CSRF (**2.1.3** y **2.1.4**). |
| **6. Login y Permisos** | *"Necesito agregar login y logout con el sistema de usuarios de Django y proteger todas las rutas de /administracion/ con @login_required y permisos, para que nadie pueda entrar ni modificar productos sin iniciar sesión."* | Restringir el acceso a las rutas críticas del CRUD y mostrar el estado de la sesión en el menú (**2.1.4**). |
| **7. Comentarios y Pruebas** | *"¿Podrías dejar comentado el código explicando qué hace cada parte para poder presentárselo al profe? Y ayúdame a armar pruebas con TestCase para verificar los filtros, el CRUD y que los permisos bloqueen bien."* | Dejar el código documentado y respaldado con pruebas automáticas contra MySQL. |

---

## 3. Problemas Encontrados, Adaptaciones y Validación

Varias cosas sugeridas por la IA no funcionaron a la primera o necesitaron ajustes manuales al probarlas en mi entorno:

### A. Configuración de MySQL y variables de entorno (Criterio 2.1.1)
* **Problema con el servidor local y las credenciales:** Al configurar `settings.py` para MySQL y correr `migrate`, arrojó el error `Can't connect to MySQL server on '127.0.0.1' (10061)` porque faltaba levantar el servicio local. Además, en la primera prueba se estaba usando el usuario `root` y la regla `.env.*` del `.gitignore` estaba ocultando también el archivo `.env.example`.
* **Cómo lo adapté:** Configuré el servicio MySQL 8.4 en local, creé un usuario exclusivo (`techstore_user`) con permisos solo sobre `techstore_db` (principio de mínimo privilegio), roté la `SECRET_KEY` y agregué la excepción `!.env.example` en `.gitignore`.
* **Validación:** Comprobé con `python manage.py check --database default` y verifiqué con `SHOW TABLES;` en MySQL Workbench que todas las tablas se crearon con `utf8mb4`.

### B. Paso a `ForeignKey` sin perder los productos (Criterio 2.1.3)
* **Problema:** Si cambiaba directamente el campo `categoria` de `CharField` a `ForeignKey` en `models.py`, Django no sabía cómo convertir textos como `"Audio"` en IDs de la nueva tabla `productos_categoria` y fallaba la migración.
* **Cómo lo adapté:** En vez de borrar la base de datos y partir de cero, dividí el cambio en 3 migraciones (`0002` a `0004`). En la migración intermedia usé `migrations.RunPython` para leer el texto antiguo de cada producto, crear su fila en `Categoria` (calculando el `slug` con `slugify`) y enlazar la clave foránea antes de borrar la columna vieja.
* **Validación:** Ejecuté `SHOW CREATE TABLE productos_producto;` en Workbench para revisar las restricciones `FOREIGN KEY` y probé en `/admin/` que al intentar borrar una categoría con productos se bloquea por `models.PROTECT`.

### C. Filtro de precios sobre productos en oferta (Criterio 2.1.3)
* **Problema:** El modelo `Producto` calcula el `precio_final` (con descuento) usando `@property` en Python. Al intentar filtrar por rango de precios en el ORM, MySQL solo miraba el precio normal de la columna `precio`, dejando fuera productos que con descuento sí entraban en el rango.
* **Cómo lo adapté:** En `productos/filtros.py` agregué una función con `annotate()`, `Case/When` y `Floor()` para que MySQL calcule `precio_final_db` directamente dentro de la consulta SQL. Además, envolví los parámetros GET en `FiltroProductosForm` para que, si alguien escribe `?precio_min=abc` en la URL, el sistema no se caiga con un error 500 sino que ignore el dato inválido y muestre un aviso.
* **Validación:** Probé en `/productos/` buscando palabras sin tilde (`inalambrico`), combinando categoría + rango de precios + check de *"Solo con stock"*, y comprobé que el conteo de resultados coincide con los precios con descuento.

### D. Seguridad en borrado, Logout y fotos del catálogo (Criterio 2.1.4)
* **Problema 1 (Logout en Django 5+):** Al probar el botón de cerrar sesión como un enlace `<a href="/usuarios/logout/">`, Django devolvió error **405 Method Not Allowed**, porque las versiones actuales exigen que el cierre de sesión sea por `POST`.
* **Problema 2 (Comentario HTML con CSRF):** En un comentario HTML (`<!-- ... -->`) dentro de una plantilla se había mencionado `{% csrf_token %}` como explicación, y Django lo estaba ejecutando igual, metiendo un input oculto extra en el HTML.
* **Problema 3 (Imágenes de prueba):** Al cargar productos adicionales sugeridos por la IA con fotos de Unsplash, revisé el catálogo en el navegador y noté que dos fotos no coincidían con el nombre del producto (un parlante decía Sony pero la foto era un JBL, y un Hub USB mostraba un escritorio).
* **Cómo lo adapté:**
  1. Cambié el botón de cerrar sesión en `base.html` por un `<form method="post">` con su `{% csrf_token %}`.
  2. Cambié los comentarios de las plantillas a `{% comment %}...{% endcomment %}` para que Django no los procese.
  3. Reemplacé manualmente las fotos y datos de los productos para que las 18 tarjetas del catálogo calzaran con su imagen real.
  4. En lugar de usar solo `is_staff`, agregué `@permission_required` en cada vista de `administracion/views.py` y creé el grupo **"Editores de catálogo"** (que puede ver, crear y editar, pero recibe **403 Prohibido** si intenta eliminar).

---

## 4. Conclusión y Reflexión Personal

Usar IA como apoyo me permitió avanzar mucho más rápido en tareas repetitivas y descubrir herramientas propias de Django que mejoraron bastante el proyecto, como el uso de `annotate(Case/When)` para calcular precios en SQL o `select_related` para evitar hacer decenas de consultas repetidas a MySQL.

Sin embargo, la experiencia demostró que **no se puede copiar y pegar sin probar**: si no hubiera revisado el navegador ni probado cada flujo, habrían quedado fotos que no correspondían a los productos, un logout que daba error 405 o filtros que calculaban mal las ofertas. La combinación de entender la lógica del código, verificar las tablas en MySQL Workbench y respaldar todo con **53 pruebas automáticas** (`python manage.py test`) fue lo que aseguró que el sistema final cumpla de verdad con los criterios de seguridad y funcionamiento.
