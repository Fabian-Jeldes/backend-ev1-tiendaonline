"""
=====================================================================
 usuarios/views.py — Autenticación de usuarios (Criterio 2.1.4)
=====================================================================

Se usan las vistas oficiales de django.contrib.auth (LoginView y LogoutView),
que ya resuelven de forma segura:
  - verificación de la contraseña contra su hash en la tabla auth_user,
  - rotación del id de sesión al iniciar sesión (evita "session fixation"),
  - validación del parámetro ?next= para no redirigir a sitios externos
    (evita "open redirect").

Solo se extienden para mostrar mensajes en español al usuario.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render

from .forms import LoginForm


class IniciarSesionView(LoginView):
    """
    GET  /usuarios/login/ -> muestra el formulario.
    POST /usuarios/login/ -> valida usuario y contraseña; si son correctos crea
                             la sesión y redirige a ?next= (la página protegida
                             que se intentó abrir) o a LOGIN_REDIRECT_URL.
    """
    template_name = 'usuarios/login.html'
    authentication_form = LoginForm
    # Si el usuario ya inició sesión y vuelve a /login/, se le redirige directamente.
    redirect_authenticated_user = True

    def form_valid(self, form):
        respuesta = super().form_valid(form)  # aquí Django ejecuta login(request, user)
        messages.success(self.request, f"¡Hola {form.get_user().get_username()}! Sesión iniciada correctamente.")
        return respuesta


class CerrarSesionView(LogoutView):
    """
    POST /usuarios/logout/ -> cierra la sesión y redirige a LOGOUT_REDIRECT_URL.

    Desde Django 5, LogoutView SOLO acepta POST (con token CSRF). Así, una página
    externa no puede cerrar tu sesión con un simple enlace o <img>. Por eso en el
    menú el botón "Cerrar sesión" es un pequeño formulario y no un <a href>.
    """

    def post(self, request, *args, **kwargs):
        respuesta = super().post(request, *args, **kwargs)  # logout(): borra la sesión en django_session
        messages.info(request, "Cerraste sesión. ¡Vuelve pronto!")
        return respuesta


@login_required
def perfil(request):
    """
    Perfil del usuario autenticado. @login_required redirige a /usuarios/login/
    si no hay sesión. Muestra qué permisos tiene sobre los productos, útil para
    demostrar el control de acceso por roles.
    """
    acciones = [
        ('view_producto', 'Ver el panel de productos'),
        ('add_producto', 'Crear productos'),
        ('change_producto', 'Editar productos'),
        ('delete_producto', 'Eliminar productos'),
    ]
    permisos = [
        (texto, request.user.has_perm(f'productos.{codigo}'))
        for codigo, texto in acciones
    ]
    contexto = {
        'titulo': 'Mi Perfil',
        'permisos': permisos,
        'grupos': request.user.groups.all(),
    }
    return render(request, 'usuarios/perfil.html', contexto)
