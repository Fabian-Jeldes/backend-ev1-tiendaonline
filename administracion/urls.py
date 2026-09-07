from django.urls import path
from . import views

urlpatterns = [
    # Panel principal de administración: /administracion/
    path('', views.panel, name='admin_panel'),
    
    # Crear un nuevo producto: /administracion/nuevo/
    path('nuevo/', views.nuevo_producto, name='admin_nuevo'),
    
    # Editar producto existente: /administracion/editar/<id>/
    path('editar/<int:id>/', views.editar_producto, name='admin_editar'),
    
    # Eliminar producto: /administracion/eliminar/<id>/
    path('eliminar/<int:id>/', views.eliminar_producto_view, name='admin_eliminar'),
]
