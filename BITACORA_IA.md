# Bitácora de Uso de Inteligencia Artificial — Evaluación 3

> **Proyecto:** TechStore Chile (Django + MySQL)
> **Asignatura:** Programación Backend (`TI3041_FB50_N4_P13_C1`) · INACAP Apoquindo · Docente Claudio Rubilar Cid
> **Criterio:** 2.1.4, *"orientaciones generadas por herramientas de inteligencia artificial"*
> **Herramienta:** Claude Code (agente de programación de Anthropic, modelo Claude Opus 5.5), usado desde la app de escritorio sobre el repositorio local
> **Fecha de trabajo:** 6 de noviembre de 2026

---

## 1. Metodología

La IA no se usó para "generar todo de una vez". El trabajo siguió un ciclo controlado:

1. **Análisis.** Se le entregó a la IA el enunciado oficial (.docx) y se le pidió comparar la rúbrica con el estado real del repositorio.
2. **División en prompts.** El trabajo pendiente se dividió en **7 prompts**, uno por funcionalidad, en un orden que respeta las dependencias. Por ejemplo, MySQL va antes que el modelo, porque las migraciones finales deben aplicarse en MySQL.
3. **Ejecución y validación por prompt.** Después de cada prompt se verificó el resultado:
   - `manage.py check` para revisar la configuración.
   - `migrate` contra MySQL.
   - Pruebas con el cliente de Django dentro de transacciones que se deshacen al final.
   - Revisión visual en el navegador.
4. **Corrección de lo que falló.** Cada error encontrado se registra en esta bitácora junto con la adaptación que se aplicó (sección 3).
5. **Pruebas automáticas.** Al final se escribieron 53 pruebas y una *prueba de mutación* para confirmar que detectan errores.

**Regla de documentación:** se le pidió a la IA que todo el código nuevo llevara comentarios didácticos en español, para poder explicarlo línea por línea en la presentación.

---

## 2. Prompts utilizados (texto exacto)

### Prompt 0: Análisis de brechas

> *"Qué cosas faltarían por agregar para cumplir con esta entrega? Y como podríamos dividr cada feature que falta en cada prompt?"* (se adjuntó el archivo `Evaluación_3_Programacion_Backend_2026_TI3041_FB50_N4_P13_C1.docx`)

**Respuesta de la IA:** comparó la rúbrica con el código y detectó lo que faltaba:
- La base de datos seguía en SQLite y la `SECRET_KEY` estaba escrita en el código.
- La categoría era un texto fijo, no una tabla relacionada.
- El catálogo no tenía filtros.
- El borrado se hacía con un GET y un `confirm()` de JavaScript.
- Las vistas de administración no tenían autenticación.
- Faltaban la bitácora y el PPT.

A partir de eso propuso los 7 prompts siguientes. Cada uno se lanzó con el mensaje *"Seguir con Prompt N"*.

| # | Prompt (texto exacto propuesto y aprobado) |
| :-: | :--- |
| 1 | *"Migra el proyecto de SQLite a MySQL usando mysqlclient (o pymysql si falla en Windows). Lee credenciales, SECRET_KEY, DEBUG y ALLOWED_HOSTS desde un .env con python-dotenv. Crea .env.example, requirements.txt, agrega .env y db.sqlite3 al .gitignore (y sácalo del repo). Documenta en el README cómo crear la BD y el usuario en MySQL y cómo correr las migraciones."* |
| 2 | *"Crea un modelo Categoria (nombre, slug, descripción) y opcionalmente Marca, y cambia Producto.categoria a ForeignKey con on_delete=PROTECT. Haz una migración de datos que convierta los choices actuales en filas de Categoria y re-asigne los productos. Actualiza admin.py, ProductoForm, plantillas y la carga de productos.json."* |
| 3 | *"En la vista catalogo agrega un formulario GET de filtros: búsqueda parcial por nombre/descripción con Q objects, categoría, precio mínimo y máximo, solo disponibles (exclude stock=0) y solo ofertas. Valida los parámetros con un forms.Form, conserva los valores en el formulario y muestra el conteo de resultados. Aplica la misma búsqueda en el panel de administración."* |
| 4 | *"Reemplaza el borrado por GET por una página de confirmación (GET muestra el producto, POST con csrf_token elimina). Usa @require_POST en la acción. Opcional: borrado lógico con campo activo, filtrado en catálogo."* |
| 5 | *"Agrega login/logout con las vistas de django.contrib.auth y una plantilla de login con el estilo del sitio. Protege todas las vistas de administracion con @login_required (y restringe a is_staff). Configura LOGIN_URL/LOGIN_REDIRECT_URL, muestra en el navbar el usuario o el botón Ingresar, y limpia la app usuarios."* |
| 6 | *"Escribe tests en Django que verifiquen: redirección a login si no hay sesión, que el CRUD funcione autenticado, que los filtros devuelvan los productos correctos y que el delete por GET no borre."* |
| 7 | *"Genera BITACORA_IA.md con cada prompt usado (texto exacto), el problema que resolvía, lo que propuso la IA, qué cambié o corregí y cómo lo validé (tests, Workbench, navegador). Luego arma un PPT de 6–8 diapositivas: contexto, conexión MySQL, modelo, CRUD+filtros, seguridad, bitácora de IA y conclusiones."* |

### Instrucciones adicionales durante el trabajo (texto exacto)

| Momento | Mensaje | Efecto |
| :--- | :--- | :--- |
| Prompt 1 | *"Instálalo con winget"* | Se autorizó instalar MySQL Server 8.4 y MySQL Workbench en el equipo. |
| Prompt 1 | *"Podrías dejar comentado el código para poder presentárselo al profe/sala de clases. Quizás una pequeña explicación de qué hace cada código"* | Desde ese momento todo el código lleva un encabezado explicativo y comentarios del *por qué*. |
| Prompt 3 | *"Las credenciales de la base de dato que no queden hardcodeadas. Podría ser? Como se debería manejar la seguridad de credenciales?"* | Se verificó que ningún archivo que se sube a git contiene secretos, y se documentaron las buenas prácticas (README §3.5). |
| Prompt 5 | *"Podrías agregar varios productos, por favor. Unos 10 o 15"* | Se agregaron 14 productos validados con `ProductoForm`, con casos de demo: 2 agotados y 9 en oferta. |
| Prompt 7 | *"Podrías usar el diseño de TBT para la presentación? Y aprovechamos de hacer una skill que sea basada en ese diseño, o ya teníamos una así?"* | La presentación se rehízo con el estilo de una presentación anterior del estudiante (paleta oscuro/marfil/dorado, League Spartan + Inter). Ese estilo quedó guardado como una skill reutilizable (`diseno-tbt`). |

---

## 3. Problemas encontrados, adaptaciones y validación

Esta es la parte central del criterio: lo que **no** funcionó a la primera y cómo se corrigió.

### Prompt 1: Conexión a MySQL

| Problema | Causa | Adaptación aplicada | Cómo se validó |
| :--- | :--- | :--- | :--- |
| `migrate` falló con `Can't connect to server on '127.0.0.1' (10061)` | MySQL no estaba instalado en el equipo. | Se instaló con `winget`. Como el instalador MSI no crea la base de datos ni el servicio, se inicializó a mano (`mysqld --initialize-insecure`) y se registró el servicio `MySQL84`, solo en `127.0.0.1`. Después se le asignó una contraseña aleatoria a root. | `Get-Service MySQL84` muestra *Running*. `SELECT VERSION()` devuelve `8.4.9`. |
| `ModuleNotFoundError: No module named 'MySQLdb'` al crear la BD | El script se ejecutó con `python -I` (modo aislado), que ignora los paquetes instalados en el usuario, donde quedó `mysqlclient`. | Se volvió a ejecutar sin `-I`. | Se creó el esquema `techstore_db` y el usuario `techstore_user`. |
| `.env.example` no aparecía en `git status` | La regla `.env.*` del `.gitignore` también ignoraba la plantilla. | Se agregó la excepción `!.env.example`. | `git status` muestra `?? .env.example`. |
| Se perderían los productos existentes al cambiar de base | Los datos estaban solo en `db.sqlite3`. | Antes del cambio se exportaron con `dumpdata` a un fixture y luego se cargaron con `loaddata`. | `Installed 4 object(s) from 1 fixture(s)`. |
| La `SECRET_KEY` antigua estaba en el historial público de GitHub | Estaba escrita en `settings.py` desde la Evaluación 1. | Se **rotó**: se generó una clave nueva que vive solo en `.env`. | La búsqueda de los valores del `.env` en los archivos versionables da 0 resultados. |
| La app usaba root | Era la práctica más simple. | Se creó `techstore_user`, con permisos solo sobre `techstore_db` (mínimo privilegio). | `CURRENT_USER()` devuelve `techstore_user@localhost`. |

### Prompt 2: Modelo relacional

| Problema | Adaptación | Validación |
| :--- | :--- | :--- |
| No se puede convertir directamente un `CharField` con datos en un `ForeignKey`: se perderían las categorías. | Se escribieron **3 migraciones manuales**: (1) crear las tablas y una FK temporal, (2) `RunPython` para crear las categorías y enlazar cada producto, (3) borrar la columna antigua y renombrar la FK. | `makemigrations --check` dice *No changes detected*. `SHOW CREATE TABLE` muestra las dos `FOREIGN KEY`. |
| En `RunPython` no existe el `save()` personalizado que genera el `slug`. | Se calcula `slugify()` dentro de la migración y se usa `apps.get_model()` (el modelo histórico). | Los slugs quedaron bien (`perifericos`, `computacion`). |
| ¿Se puede deshacer la migración? | Se agregó una función inversa (`deshacer`). | Se revirtió hasta `0001` y se volvió a aplicar: los 4 productos quedaron con la misma categoría y marca. |
| Los mensajes de error salían en inglés (*"Select a valid choice"*). | Se cambió a `LANGUAGE_CODE='es-cl'` y `TIME_ZONE='America/Santiago'`. | El error ahora dice *"Escoja una opción válida…"*. |

Además se probaron `PROTECT` (borrar una categoría con productos lanza `ProtectedError`), `SET_NULL` (borrar una marca deja `marca=None`) y la relación inversa, dentro de una transacción que se deshizo al terminar.

### Prompt 3: Filtros con el ORM

| Problema | Adaptación | Validación |
| :--- | :--- | :--- |
| El rango de precio debía usar el precio **con descuento**, pero `precio_final` es una `@property` de Python y MySQL no la conoce. | `annotate()` con `Case/When` para que MySQL calcule `precio_final_db`. Se usó `Floor()` para replicar el `int()` de la propiedad y que no haya diferencias de $1. | Para los productos se comparó `precio_final` (Python) con `precio_final_db` (MySQL): **todos coinciden**. |
| Un valor inválido en la URL (`?precio_min=abc`) podía romper la consulta. | Se validan los filtros con `forms.Form`. Se ignora solo el filtro malo y se muestra el error. | `?precio_min=abc&ofertas=on` aplica solo el filtro de ofertas y muestra *"Introduzca un número entero"*. |
| La primera versión de la vista leía los datos con una expresión difícil de explicar. | Se refactorizó en un método `datos_validos()` con su docstring. | Mismos resultados en 12 combinaciones de filtros. |

Hallazgo útil para la presentación: gracias a la collation `utf8mb4_unicode_ci` de MySQL, buscar `inalambrico` (sin tilde) encuentra "Inalámbrico".

### Prompt 4: Borrado seguro

| Problema | Adaptación | Validación |
| :--- | :--- | :--- |
| El borrado por GET era vulnerable a CSRF (`<img src=".../eliminar/5/">`) y el `confirm()` de JavaScript se podía saltar. | Se usan dos pasos: el GET muestra la confirmación y el POST con `{% csrf_token %}` borra. `@require_http_methods(['GET','POST'])` rechaza los demás métodos. Se aplicó el patrón Post/Redirect/Get. | GET → 200 y no borra. POST sin token → **403**. DELETE → **405**. POST válido → 302 y borra. Id inexistente → 404. |
| Un comentario HTML (`<!-- -->`) que mencionaba `{% csrf_token %}` se **renderizaba igual**, porque Django procesa las etiquetas dentro de los comentarios HTML. | Se cambió por `{% comment %}…{% endcomment %}`, que Django no procesa. | El código fuente de la página ya no muestra un token de más. |

### Prompt 5: Autenticación y permisos

| Problema | Adaptación | Validación |
| :--- | :--- | :--- |
| El prompt pedía `is_staff`, pero eso no distingue entre acciones. | Se usó `@permission_required` con el permiso de cada acción (`view`, `add`, `change`, `delete`) y se creó el grupo **Editores de catálogo**, sin `delete`. | Anónimo → login. Sin permisos → 403. Editor → 200/200/200/**403**. Superusuario → todo 200. |
| En una migración los permisos todavía no existen (Django los crea después, con `post_migrate`). | Se llama a `create_permissions()` dentro de la migración del grupo. | `python manage.py test` crea una base nueva desde cero y el grupo aparece con sus 3 permisos. |
| Desde Django 5, `LogoutView` no acepta GET. | "Cerrar sesión" es un `<form method="post">` con CSRF, no un enlace. | Logout por GET → **405**. Por POST → 302 y la sesión se cierra. |
| La primera verificación de la página 403 dio un falso negativo (`DisallowedHost`). | Fue un error de la prueba, no de la app: faltaba `setup_test_environment()`, que habilita el host `testserver`. | Al repetirla se confirmó que se usa `403.html`. |
| Al agregar productos, 2 fotos de Unsplash no correspondían: el "parlante Sony" mostraba un **JBL** y el "hub USB-C" mostraba un escritorio gamer. | Se detectó **revisando visualmente** el catálogo. El parlante se cambió a *JBL Flip 6* y el hub se reemplazó por una tarjeta de video RTX 4060 que sí coincide con su foto. | Se revisaron las 18 tarjetas del catálogo en el navegador. |

### Prompt 6: Pruebas automáticas

- **53 pruebas** en tres archivos. Pasan todas contra MySQL en unos 5 s (`Ran 53 tests ... OK`).
- **Prueba de mutación:** se quitaron a propósito los decoradores de seguridad de `eliminar_producto_view`. **Fallaron 5 pruebas**, todas sobre esa ruta. Al restaurar el código volvieron a pasar. Esto demuestra que las pruebas sí detectan si alguien elimina la protección.

---

## 4. Análisis crítico del uso de IA

**Lo que la IA hizo bien:**
- Leyó la rúbrica y el código, y propuso un plan dividido en pasos que se pueden verificar por separado.
- Propuso soluciones más completas que las pedidas: por ejemplo, permisos por acción en vez de solo `is_staff`, y `annotate()` para filtrar por el precio final.
- Ante cada error, diagnosticó la causa en lugar de probar a ciegas.

**Lo que requirió control humano o verificación:**
- **La IA no sabía que MySQL no estaba instalado.** Su primera versión era correcta en el código, pero no funcionaba en el equipo. Hubo que decidir instalarlo, y esa decisión la tomó el estudiante.
- **Contenido no verificable:** la IA elige URLs de imágenes sin poder saber qué muestran. Comprobar que respondieran (HTTP 200) **no bastó**: hubo que mirarlas.
- **Supuestos del framework que cambian entre versiones:** que `LogoutView` sea solo POST, o que Django procese etiquetas dentro de comentarios HTML. Se detectaron al probar, no al leer el código.
- **Sus propias pruebas también pueden fallar:** el falso negativo de `DisallowedHost` muestra que hay que entender por qué falla una prueba antes de "arreglar" el código.

**Conclusión:** la IA aceleró mucho el trabajo, pero el resultado es confiable por la **validación**: las migraciones se revirtieron y volvieron a aplicar, se compararon los valores de Python con los de MySQL, se probaron los códigos HTTP (302, 403, 405, 404), se revisó el resultado visualmente y se dejaron pruebas automáticas con prueba de mutación. Ningún cambio se aceptó sin una evidencia de que funciona.

---

## 5. Reflexión personal (completar por el estudiante)

> Esta sección es para tus propias palabras: el profesor evalúa *tu* comprensión. Sugerencias:
> - ¿Qué parte del código podrías explicar sin mirar los comentarios? ¿Cuál te costó más entender?
> - ¿Qué habría pasado si aceptabas la primera versión sin probarla (por ejemplo, las fotos o el borrado por GET)?
> - ¿Qué harías distinto en un proyecto real (por ejemplo, borrado lógico, HTTPS, límite de intentos de login)?

*…*
