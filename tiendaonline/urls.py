from django.contrib import admin
from django.urls import path, include
from productos import views as productos_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', productos_views.inicio, name='inicio'),
    path('productos/', include('productos.urls')),
    path('contacto/', productos_views.contacto, name='contacto'),
    path('administracion/', include('administracion.urls')),
]
