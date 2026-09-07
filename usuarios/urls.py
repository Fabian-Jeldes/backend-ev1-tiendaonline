from django.urls import path
from . import views

urlpatterns = [
    # Ruta: /usuarios/registro/ -> Formulario de registro de clientes
    path('registro/', views.registro, name='registro'),
    
    # Ruta: /usuarios/perfil/ -> Visualización del perfil del cliente
    path('perfil/', views.perfil, name='perfil'),
]
