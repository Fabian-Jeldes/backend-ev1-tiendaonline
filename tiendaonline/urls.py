"""
Tabla principal de rutas del proyecto.
Cada include() delega un prefijo de URL a las rutas de una app.
"""

from django.contrib import admin
from django.urls import path, include
from productos import views as productos_views

urlpatterns = [
    path('admin/', admin.site.urls),                            # Admin oficial de Django (solo staff)
    path('', productos_views.inicio, name='inicio'),            # Portada pública
    path('productos/', include('productos.urls')),              # Catálogo público con filtros
    path('contacto/', productos_views.contacto, name='contacto'),
    path('administracion/', include('administracion.urls')),    # CRUD protegido con login + permisos
    path('usuarios/', include('usuarios.urls')),                # Login, logout y perfil
]
