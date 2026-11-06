"""
=====================================================================
 productos/tests.py — Pruebas automáticas de modelos y filtros
=====================================================================

Cómo ejecutarlas:   python manage.py test
                    python manage.py test productos      (solo esta app)

Django crea una base de datos TEMPORAL en MySQL (test_techstore_db), aplica
todas las migraciones, ejecuta cada prueba dentro de una transacción que se
deshace al terminar y, al final, borra la base temporal. Los datos reales
de techstore_db nunca se tocan.

Cada método test_* es una prueba independiente. Los self.assert...()
comprueban que el resultado sea el esperado; si alguno falla, Django
informa qué prueba falló y por qué.
"""

from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from .filtros import FiltroProductosForm, aplicar_filtros
from .models import Categoria, Marca, Producto


def crear_producto(nombre, categoria, **extra):
    """Atajo para crear productos de prueba con valores por defecto válidos."""
    datos = {
        'precio': 10000,
        'stock': 5,
        'descripcion': 'Producto de prueba para tests automáticos.',
        'imagen': 'https://example.com/imagen.jpg',
    }
    datos.update(extra)
    return Producto.objects.create(nombre=nombre, categoria=categoria, **datos)


class ModeloRelacionalTests(TestCase):
    """Criterio 2.1.3: modelo con varias clases relacionadas por ForeignKey."""

    @classmethod
    def setUpTestData(cls):
        # Las categorías y marcas ya existen: las creó la migración de datos 0003.
        # Que estas consultas funcionen prueba también que esa migración se aplicó bien.
        cls.audio = Categoria.objects.get(slug='audio')
        cls.sony = Marca.objects.get(nombre='Sony')
        cls.producto = crear_producto('Audífonos de prueba', cls.audio, marca=cls.sony)

    def test_migracion_creo_las_categorias_iniciales(self):
        self.assertEqual(Categoria.objects.count(), 6)
        self.assertTrue(Categoria.objects.filter(slug='perifericos').exists())

    def test_slug_se_genera_automaticamente(self):
        categoria = Categoria.objects.create(nombre='Cámaras Web')
        self.assertEqual(categoria.slug, 'camaras-web')

    def test_relacion_inversa_related_name(self):
        # categoria.productos.all() funciona gracias a related_name='productos'.
        self.assertIn(self.producto, self.audio.productos.all())
        self.assertIn(self.producto, self.sony.productos.all())

    def test_protect_impide_borrar_categoria_con_productos(self):
        with self.assertRaises(ProtectedError):
            self.audio.delete()
        self.assertTrue(Categoria.objects.filter(pk=self.audio.pk).exists())

    def test_set_null_al_borrar_marca_conserva_el_producto(self):
        self.sony.delete()
        self.producto.refresh_from_db()  # vuelve a leer la fila desde MySQL
        self.assertIsNone(self.producto.marca)

    def test_precio_final_con_descuento(self):
        p = crear_producto('Oferta', self.audio, precio=99990, oferta=True, descuento=20)
        self.assertEqual(p.ahorro, 19998)
        self.assertEqual(p.precio_final, 79992)
        self.assertEqual(p.precio_final_formateado, '$79.992')

    def test_sin_oferta_el_descuento_no_se_aplica(self):
        p = crear_producto('Normal', self.audio, precio=50000, oferta=False, descuento=30)
        self.assertEqual(p.precio_final, 50000)


class FiltrosCatalogoTests(TestCase):
    """Criterio 2.1.3: filtros con filter(), exclude(), Q objects y annotate()."""

    @classmethod
    def setUpTestData(cls):
        audio = Categoria.objects.get(slug='audio')
        perifericos = Categoria.objects.get(slug='perifericos')
        logitech = Marca.objects.get(nombre='Logitech')
        cls.teclado = crear_producto('Teclado Mecánico Inalámbrico', perifericos, marca=logitech,
                                     precio=100000, oferta=True, descuento=20, stock=10)   # final 80.000
        cls.mouse = crear_producto('Mouse Óptico', perifericos, marca=logitech,
                                   precio=20000, stock=0)                                  # agotado
        cls.parlante = crear_producto('Parlante Inalámbrico', audio,
                                      precio=60000, stock=3,
                                      descripcion='Sonido potente con bluetooth.')

    def filtrar(self, **parametros):
        """Simula la barra de filtros: valida los parámetros y devuelve la lista resultante."""
        form = FiltroProductosForm(parametros)
        return list(aplicar_filtros(Producto.objects.all(), form.datos_validos())), form

    def test_sin_filtros_devuelve_todo(self):
        productos, _ = self.filtrar()
        self.assertEqual(len(productos), 3)

    def test_busqueda_parcial_por_nombre(self):
        productos, _ = self.filtrar(q='teclado')
        self.assertEqual(productos, [self.teclado])

    def test_busqueda_varias_palabras_exige_todas(self):
        productos, _ = self.filtrar(q='inalámbrico parlante')
        self.assertEqual(productos, [self.parlante])

    def test_busqueda_ignora_tildes_y_mayusculas(self):
        # Gracias a la collation utf8mb4_unicode_ci de MySQL.
        productos, _ = self.filtrar(q='INALAMBRICO')
        self.assertCountEqual(productos, [self.teclado, self.parlante])

    def test_busqueda_en_descripcion_y_marca(self):
        self.assertEqual(self.filtrar(q='bluetooth')[0], [self.parlante])
        self.assertCountEqual(self.filtrar(q='logitech')[0], [self.teclado, self.mouse])

    def test_filtro_por_categoria_slug(self):
        productos, _ = self.filtrar(categoria='audio')
        self.assertEqual(productos, [self.parlante])

    def test_rango_de_precio_usa_precio_final(self):
        # El teclado cuesta 100.000 pero con 20% queda en 80.000 -> entra en el rango.
        productos, _ = self.filtrar(precio_min=70000, precio_max=90000)
        self.assertEqual(productos, [self.teclado])

    def test_solo_disponibles_excluye_agotados(self):
        productos, _ = self.filtrar(disponibles='on')
        self.assertNotIn(self.mouse, productos)
        self.assertEqual(len(productos), 2)

    def test_solo_ofertas(self):
        productos, _ = self.filtrar(ofertas='on')
        self.assertEqual(productos, [self.teclado])

    def test_orden_por_precio_ascendente(self):
        productos, _ = self.filtrar(orden='precio_asc')
        self.assertEqual(productos, [self.mouse, self.parlante, self.teclado])

    def test_filtros_combinados(self):
        productos, _ = self.filtrar(categoria='perifericos', disponibles='on', q='mecánico')
        self.assertEqual(productos, [self.teclado])

    def test_precio_invalido_se_ignora_y_muestra_error(self):
        productos, form = self.filtrar(precio_min='abc', ofertas='on')
        self.assertIn('precio_min', form.errors)
        self.assertEqual(productos, [self.teclado])  # el filtro de ofertas sí se aplicó

    def test_minimo_mayor_que_maximo_es_error(self):
        _, form = self.filtrar(precio_min=90000, precio_max=1000)
        self.assertIn('precio_max', form.errors)

    def test_categoria_inexistente_es_error(self):
        _, form = self.filtrar(categoria='no-existe')
        self.assertIn('categoria', form.errors)

    def test_vista_catalogo_publica_con_filtros(self):
        respuesta = self.client.get(reverse('catalogo'), {'q': 'mouse'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context['productos']), [self.mouse])
        self.assertEqual(respuesta.context['total_filtrados'], 1)
        self.assertContains(respuesta, 'Mouse Óptico')
        self.assertNotContains(respuesta, 'Parlante Inalámbrico')
