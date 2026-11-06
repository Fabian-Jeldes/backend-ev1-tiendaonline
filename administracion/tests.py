"""
=====================================================================
 administracion/tests.py — Pruebas del CRUD y de su seguridad
=====================================================================

Prueban dos cosas:
  1. CRUD (Criterio 2.1.3): crear, listar, editar y eliminar funcionan.
  2. Seguridad (Criterio 2.1.4): ninguna ruta de administración se puede
     usar sin sesión ni sin el permiso correspondiente, y el borrado exige
     POST con token CSRF.

self.client es un navegador simulado: hace peticiones GET/POST a las vistas
sin levantar un servidor. force_login() inicia sesión sin pasar por el
formulario de login (eso se prueba aparte en usuarios/tests.py).
"""

from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse

from productos.models import Categoria, Marca, Producto


class BaseAdministracionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categoria = Categoria.objects.get(slug='perifericos')
        cls.marca = Marca.objects.get(nombre='Logitech')
        cls.producto = Producto.objects.create(
            nombre='Mouse Inalámbrico de Prueba', categoria=cls.categoria, marca=cls.marca,
            precio=25000, stock=8, descripcion='Mouse de prueba para tests.',
            imagen='https://example.com/mouse.jpg',
        )
        # Tres perfiles de usuario para probar el control de acceso.
        cls.sin_permisos = User.objects.create_user('cliente')
        cls.editor = User.objects.create_user('editor')
        cls.editor.groups.add(Group.objects.get(name='Editores de catálogo'))
        cls.admin = User.objects.create_superuser('admin')

    def rutas(self):
        """Las 4 rutas del CRUD con el permiso que exige cada una."""
        pk = self.producto.pk
        return {
            'panel': reverse('admin_panel'),
            'nuevo': reverse('admin_nuevo'),
            'editar': reverse('admin_editar', args=[pk]),
            'eliminar': reverse('admin_eliminar', args=[pk]),
        }

    def datos_validos(self, **cambios):
        datos = {
            'nombre': 'Teclado Nuevo de Prueba', 'categoria': self.categoria.pk, 'marca': self.marca.pk,
            'precio': 45990, 'stock': 12, 'descuento': 0,
            'imagen': 'https://example.com/teclado.jpg',
            'descripcion': 'Teclado creado desde el test del CRUD.',
        }
        datos.update(cambios)
        return datos


class ControlDeAccesoTests(BaseAdministracionTest):
    """Criterio 2.1.4: rutas críticas protegidas con login y permisos."""

    def test_anonimo_es_redirigido_al_login_en_todas_las_rutas(self):
        for nombre, url in self.rutas().items():
            with self.subTest(ruta=nombre):
                respuesta = self.client.get(url)
                # 302 hacia /usuarios/login/?next=<ruta original>
                self.assertRedirects(respuesta, f"{reverse('login')}?next={url}")

    def test_anonimo_no_puede_eliminar_por_post(self):
        self.client.post(self.rutas()['eliminar'])
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_anonimo_no_puede_crear_por_post(self):
        self.client.post(self.rutas()['nuevo'], self.datos_validos())
        self.assertFalse(Producto.objects.filter(nombre='Teclado Nuevo de Prueba').exists())

    def test_usuario_sin_permisos_recibe_403(self):
        self.client.force_login(self.sin_permisos)
        for nombre, url in self.rutas().items():
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_editor_puede_ver_crear_y_editar_pero_no_eliminar(self):
        self.client.force_login(self.editor)
        esperado = {'panel': 200, 'nuevo': 200, 'editar': 200, 'eliminar': 403}
        for nombre, url in self.rutas().items():
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(url).status_code, esperado[nombre])
        self.client.post(self.rutas()['eliminar'])
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_superusuario_accede_a_todo(self):
        self.client.force_login(self.admin)
        for nombre, url in self.rutas().items():
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_pagina_403_personalizada(self):
        self.client.force_login(self.sin_permisos)
        respuesta = self.client.get(self.rutas()['panel'])
        self.assertTemplateUsed(respuesta, '403.html')


class CrudProductosTests(BaseAdministracionTest):
    """Criterio 2.1.3: las 4 operaciones CRUD contra MySQL."""

    def setUp(self):
        self.client.force_login(self.admin)

    def test_create_guarda_el_producto(self):
        respuesta = self.client.post(self.rutas()['nuevo'], self.datos_validos())
        self.assertRedirects(respuesta, reverse('admin_panel'))
        creado = Producto.objects.get(nombre='Teclado Nuevo de Prueba')
        self.assertEqual(creado.categoria, self.categoria)
        self.assertEqual(creado.marca, self.marca)

    def test_create_rechaza_datos_invalidos(self):
        respuesta = self.client.post(self.rutas()['nuevo'], self.datos_validos(precio=100, nombre='ab'))
        self.assertEqual(respuesta.status_code, 200)  # vuelve a mostrar el formulario con errores
        self.assertIn('precio', respuesta.context['form'].errors)
        self.assertIn('nombre', respuesta.context['form'].errors)
        self.assertEqual(Producto.objects.count(), 1)

    def test_create_rechaza_categoria_inexistente(self):
        respuesta = self.client.post(self.rutas()['nuevo'], self.datos_validos(categoria=999999))
        self.assertIn('categoria', respuesta.context['form'].errors)

    def test_read_panel_lista_productos(self):
        respuesta = self.client.get(self.rutas()['panel'])
        self.assertContains(respuesta, 'Mouse Inalámbrico de Prueba')
        self.assertEqual(respuesta.context['total_productos'], 1)

    def test_read_panel_con_filtro(self):
        respuesta = self.client.get(self.rutas()['panel'], {'q': 'no-coincide'})
        self.assertEqual(respuesta.context['total_filtrados'], 0)

    def test_update_modifica_el_producto(self):
        url = self.rutas()['editar']
        self.client.post(url, self.datos_validos(nombre='Mouse Editado', stock=3))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Mouse Editado')
        self.assertEqual(self.producto.stock, 3)

    def test_delete_get_solo_muestra_confirmacion(self):
        respuesta = self.client.get(self.rutas()['eliminar'])
        self.assertTemplateUsed(respuesta, 'administracion/confirmar_eliminar.html')
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_delete_post_elimina_el_producto(self):
        respuesta = self.client.post(self.rutas()['eliminar'])
        self.assertRedirects(respuesta, reverse('admin_panel'))
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_delete_otro_metodo_http_responde_405(self):
        self.assertEqual(self.client.delete(self.rutas()['eliminar']).status_code, 405)

    def test_producto_inexistente_responde_404(self):
        self.assertEqual(self.client.get(reverse('admin_editar', args=[999999])).status_code, 404)


class ProteccionCsrfTests(BaseAdministracionTest):
    """
    Criterio 2.1.4: el cliente de pruebas normalmente omite el chequeo CSRF.
    Con enforce_csrf_checks=True se comporta como un navegador real.
    """

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.admin)

    def test_post_sin_token_csrf_es_rechazado(self):
        respuesta = self.client.post(self.rutas()['eliminar'])
        self.assertEqual(respuesta.status_code, 403)
        self.assertTrue(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_post_con_token_csrf_es_aceptado(self):
        # 1) GET a la confirmación: Django entrega el token en una cookie y en el formulario.
        self.client.get(self.rutas()['eliminar'])
        token = self.client.cookies['csrftoken'].value
        # 2) POST enviando ese token, igual que el <form> del navegador.
        respuesta = self.client.post(self.rutas()['eliminar'], {'csrfmiddlewaretoken': token})
        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(Producto.objects.filter(pk=self.producto.pk).exists())

    def test_formularios_incluyen_token_csrf(self):
        for nombre in ('nuevo', 'editar', 'eliminar'):
            with self.subTest(formulario=nombre):
                self.assertContains(self.client.get(self.rutas()[nombre]), 'csrfmiddlewaretoken')
