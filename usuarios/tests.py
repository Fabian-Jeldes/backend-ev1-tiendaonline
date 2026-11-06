"""
=====================================================================
 usuarios/tests.py — Pruebas de inicio y cierre de sesión
=====================================================================
Prueban el flujo REAL de login con usuario y contraseña (no force_login),
el logout seguro y las protecciones de LoginView.
"""

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

CLAVE = 'Clave-Segura-De-Prueba-2026'


class LoginLogoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuario = User.objects.create_user('vendedor', password=CLAVE)
        cls.usuario.groups.add(Group.objects.get(name='Editores de catálogo'))

    def test_contrasena_se_guarda_con_hash(self):
        # La contraseña nunca se guarda en texto plano en la tabla auth_user.
        self.assertNotEqual(self.usuario.password, CLAVE)
        self.assertTrue(self.usuario.password.startswith('pbkdf2_sha256$'))

    def test_pagina_de_login_tiene_csrf(self):
        respuesta = self.client.get(reverse('login'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'csrfmiddlewaretoken')

    def test_login_correcto_redirige_al_panel(self):
        respuesta = self.client.post(reverse('login'), {'username': 'vendedor', 'password': CLAVE})
        self.assertRedirects(respuesta, reverse('admin_panel'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.usuario.pk)

    def test_login_vuelve_a_la_pagina_next(self):
        destino = reverse('admin_nuevo')
        respuesta = self.client.post(
            f"{reverse('login')}?next={destino}",
            {'username': 'vendedor', 'password': CLAVE, 'next': destino},
        )
        self.assertRedirects(respuesta, destino)

    def test_login_bloquea_redireccion_a_sitio_externo(self):
        respuesta = self.client.post(
            reverse('login'),
            {'username': 'vendedor', 'password': CLAVE, 'next': 'https://sitio-malicioso.com/'},
        )
        self.assertRedirects(respuesta, reverse('admin_panel'))

    def test_login_incorrecto_muestra_error_generico(self):
        respuesta = self.client.post(reverse('login'), {'username': 'vendedor', 'password': 'incorrecta'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Usuario o contraseña incorrectos')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_por_get_no_esta_permitido(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)

    def test_logout_por_post_cierra_la_sesion(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse('logout'))
        self.assertRedirects(respuesta, reverse('inicio'))
        # Tras cerrar sesión, el panel vuelve a pedir login.
        self.assertEqual(self.client.get(reverse('admin_panel')).status_code, 302)

    def test_perfil_requiere_login(self):
        respuesta = self.client.get(reverse('perfil'))
        self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse('perfil')}")

    def test_perfil_muestra_permisos_del_grupo(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse('perfil'))
        permisos = dict(respuesta.context['permisos'])
        self.assertTrue(permisos['Editar productos'])
        self.assertFalse(permisos['Eliminar productos'])

    def test_navbar_muestra_ingresar_o_usuario(self):
        self.assertContains(self.client.get(reverse('inicio')), 'Ingresar')
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse('inicio'))
        self.assertContains(respuesta, 'vendedor')
        self.assertContains(respuesta, 'Admin Productos')
