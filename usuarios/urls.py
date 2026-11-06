"""Rutas de autenticación: /usuarios/login/, /usuarios/logout/ y /usuarios/perfil/."""

from django.urls import path

from . import views

urlpatterns = [
    # Formulario de inicio de sesión (GET muestra, POST autentica).
    path('login/', views.IniciarSesionView.as_view(), name='login'),

    # Cierre de sesión (solo POST con token CSRF).
    path('logout/', views.CerrarSesionView.as_view(), name='logout'),

    # Perfil del usuario autenticado (protegido con @login_required).
    path('perfil/', views.perfil, name='perfil'),
]
