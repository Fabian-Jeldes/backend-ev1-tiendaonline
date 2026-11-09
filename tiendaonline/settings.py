"""
=====================================================================
 settings.py — Configuración central del proyecto TechStore (Django)
=====================================================================

Este archivo le dice a Django CÓMO debe funcionar el proyecto:
  - qué aplicaciones están instaladas,
  - a qué base de datos se conecta (en esta entrega: MySQL),
  - dónde están las plantillas HTML y los archivos estáticos,
  - y parámetros de seguridad como la SECRET_KEY o DEBUG.

IDEA CLAVE DE SEGURIDAD (Criterio 2.1.1):
  Ninguna contraseña ni clave secreta está escrita en este archivo.
  Todas se leen desde un archivo ".env" que vive solo en el computador
  local y que está excluido de git (ver .gitignore). En el repositorio
  solo se sube ".env.example", una plantilla SIN valores reales.

Documentación oficial: https://docs.djangoproject.com/en/6.1/ref/settings/
"""

import os                      # Para leer variables de entorno del sistema (os.getenv)
from pathlib import Path       # Para construir rutas de carpetas de forma segura en Windows/Linux

from django.core.exceptions import ImproperlyConfigured  # Error estándar de Django para configuración inválida
from dotenv import load_dotenv  # Librería python-dotenv: carga el archivo .env como variables de entorno


# ---------------------------------------------------------------------
# 1. RUTA BASE DEL PROYECTO
# ---------------------------------------------------------------------
# __file__ es este archivo (tiendaonline/settings.py). Subimos dos niveles
# (.parent.parent) para llegar a la carpeta raíz, donde está manage.py.
# Todas las demás rutas (templates, static, .env) se arman desde aquí.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------
# 2. CARGA DE VARIABLES DE ENTORNO (.env)
# ---------------------------------------------------------------------
# load_dotenv lee cada línea "CLAVE=valor" del archivo .env y la deja
# disponible para os.getenv("CLAVE"). Así separamos el CÓDIGO (público,
# en git) de las CREDENCIALES (privadas, solo en cada máquina).
load_dotenv(BASE_DIR / '.env')


def env_requerida(nombre):
    """
    Lee una variable de entorno OBLIGATORIA.

    Si la variable no existe o está vacía, detiene el arranque de Django
    con un mensaje claro, en lugar de fallar más tarde con un error confuso
    (por ejemplo, un "Access denied" de MySQL sin saber por qué).

    Ejemplo: env_requerida('DB_NAME')  ->  'techstore_db'
    """
    valor = os.getenv(nombre)
    if not valor:
        raise ImproperlyConfigured(
            f"Falta la variable de entorno '{nombre}'. Cópiala desde .env.example a tu archivo .env."
        )
    return valor


# ---------------------------------------------------------------------
# 3. SEGURIDAD BÁSICA
# ---------------------------------------------------------------------
# SECRET_KEY: Django la usa para firmar cookies de sesión y los tokens CSRF
# de los formularios. Si alguien la conoce, podría falsificar sesiones,
# por eso es obligatoria y se lee desde .env (nunca escrita aquí).
SECRET_KEY = env_requerida('DJANGO_SECRET_KEY')

# DEBUG: en True muestra páginas de error detalladas (útil al programar).
# En producción debe ser False, porque esas páginas exponen código y datos.
# Por defecto es False (opción segura); el .env local lo activa con True.
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() in ('true', '1', 'yes')

# ALLOWED_HOSTS: dominios desde los que se puede acceder al sitio.
# Antes era ['*'] (cualquiera); ahora es una lista explícita separada por comas.
# Ejemplo en .env:  DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]


# ---------------------------------------------------------------------
# 4. APLICACIONES INSTALADAS
# ---------------------------------------------------------------------
# Las primeras son apps que trae Django (admin, autenticación, sesiones...).
# Las últimas son las apps propias de TechStore.
INSTALLED_APPS = [
    'django.contrib.admin',          # Panel /admin/ oficial de Django
    'django.contrib.auth',           # Usuarios, contraseñas, login y permisos
    'django.contrib.contenttypes',   # Registro interno de los modelos (lo usan admin y auth)
    'django.contrib.sessions',       # Sesiones: recordar al usuario entre páginas
    'django.contrib.messages',       # Mensajes flash ("Producto guardado con éxito")
    'django.contrib.staticfiles',    # Servir CSS, JS e imágenes
    'productos',                     # catálogo, detalle y contacto
    'administracion',                # CRUD de productos
    'usuarios',                      # login, logout, perfil y grupo de permisos
]


# ---------------------------------------------------------------------
# 5. MIDDLEWARE (filtros que procesan cada petición y respuesta)
# ---------------------------------------------------------------------
# Se ejecutan en orden en cada request. Los más importantes para seguridad:
#   - CsrfViewMiddleware: rechaza formularios POST sin {% csrf_token %} válido.
#   - XFrameOptionsMiddleware: impide que el sitio se cargue dentro de un
#     <iframe> ajeno (protección contra "clickjacking").
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Archivo con la tabla principal de rutas (URLs) del sitio.
ROOT_URLCONF = 'tiendaonline.urls'


# ---------------------------------------------------------------------
# 6. PLANTILLAS HTML
# ---------------------------------------------------------------------
# DIRS: carpeta global "templates/" en la raíz del proyecto.
# APP_DIRS: además busca una carpeta "templates/" dentro de cada app.
# context_processors: variables disponibles en TODAS las plantillas
# (por ejemplo {{ user }} y {{ messages }}).
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Punto de entrada del servidor web (lo usa runserver y servidores como gunicorn).
WSGI_APPLICATION = 'tiendaonline.wsgi.application'


# ---------------------------------------------------------------------
# 7. BASE DE DATOS: MySQL (Criterio 2.1.1)
# ---------------------------------------------------------------------
# En la evaluación anterior se usaba SQLite (un archivo db.sqlite3).
# Ahora el proyecto se conecta a un SERVIDOR MySQL externo.
#
# ENGINE 'django.db.backends.mysql' usa por debajo el conector "mysqlclient"
# (instalado con: pip install mysqlclient), que es el recomendado por Django.
#
# Cada parámetro sale del archivo .env:
#   DB_NAME     -> nombre del esquema en MySQL     (ej: techstore_db)
#   DB_USER     -> usuario de MySQL para la app    (ej: techstore_user, NO root)
#   DB_PASSWORD -> contraseña de ese usuario
#   DB_HOST     -> dirección del servidor          (127.0.0.1 = este mismo PC)
#   DB_PORT     -> puerto de MySQL                 (3306 es el estándar)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env_requerida('DB_NAME'),
        'USER': env_requerida('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            # utf8mb4 = UTF-8 completo: guarda bien tildes, ñ y emojis.
            # (El "utf8" antiguo de MySQL no soporta todos los caracteres.)
            'charset': 'utf8mb4',
            # Modo estricto: si llega un dato inválido (texto demasiado largo,
            # número fuera de rango), MySQL lanza error en vez de recortarlo
            # en silencio. Así se protege la integridad de los datos.
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        # Configuración de la base de datos temporal que crea "manage.py test".
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    }
}


# ---------------------------------------------------------------------
# 8. VALIDACIÓN DE CONTRASEÑAS DE USUARIOS
# ---------------------------------------------------------------------
# Reglas que Django aplica al crear o cambiar contraseñas:
# no parecida al nombre de usuario, largo mínimo, no ser una contraseña
# común (ej. "123456") y no ser solo números.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ---------------------------------------------------------------------
# 8.1 AUTENTICACIÓN Y SESIONES (Criterio 2.1.4)
# ---------------------------------------------------------------------
# LOGIN_URL: adónde @login_required envía a quien no inició sesión.
#   Se agrega ?next=/ruta/original/ para volver ahí después del login.
LOGIN_URL = 'login'
# Destino tras iniciar sesión cuando no hay ?next= (el panel de productos).
LOGIN_REDIRECT_URL = 'admin_panel'
# Destino tras cerrar sesión.
LOGOUT_REDIRECT_URL = 'inicio'

# La sesión expira tras 2 horas o al cerrar el navegador, lo que ocurra primero.
# Limita el riesgo si alguien deja la sesión abierta en un computador compartido.
SESSION_COOKIE_AGE = 60 * 60 * 2
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# HttpOnly (por defecto True en Django): JavaScript no puede leer la cookie de
# sesión, así un ataque XSS no puede robarla. Se deja explícito para documentarlo.
SESSION_COOKIE_HTTPONLY = True


# ---------------------------------------------------------------------
# 9. IDIOMA Y ZONA HORARIA
# ---------------------------------------------------------------------
# LANGUAGE_CODE 'es-cl': mensajes de Django (errores de formularios, /admin/) en español.
# USE_TZ = True: las fechas se guardan en la base de datos en UTC
# y Django las convierte a la hora de Chile (TIME_ZONE) al mostrarlas.
LANGUAGE_CODE = 'es-cl'

TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------
# 10. ARCHIVOS ESTÁTICOS (CSS, JavaScript, imágenes)
# ---------------------------------------------------------------------
# STATIC_URL: prefijo en la URL  (ej: /static/css/estilos.css)
# STATICFILES_DIRS: carpeta física donde están esos archivos.
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']


# ---------------------------------------------------------------------
# 11. CORREO ELECTRÓNICO
# ---------------------------------------------------------------------
# En desarrollo los correos no se envían: se imprimen en la consola.
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
