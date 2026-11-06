"""
=====================================================================
 productos/filtros.py — Búsqueda y filtrado dinámico (Criterio 2.1.3)
=====================================================================

Este módulo tiene dos piezas que usan el catálogo público (/productos/)
y el panel de administración (/administracion/):

  1. FiltroProductosForm: valida lo que el usuario escribe en la barra de
     filtros (parámetros GET de la URL, ej: ?q=teclado&precio_max=100000).
  2. aplicar_filtros(): traduce esos datos válidos a consultas del ORM
     de Django (filter, exclude, Q objects, annotate, order_by), que Django
     convierte en un SELECT ... WHERE ... ORDER BY para MySQL.

¿Por qué validar con un formulario si es solo una búsqueda?
  Porque los parámetros GET vienen del usuario y se pueden manipular a
  mano en la URL (?precio_min=abc, ?categoria=no-existe). El formulario
  descarta los valores inválidos antes de que lleguen a la base de datos.
"""

from django import forms
from django.db.models import Case, F, IntegerField, Q, When
from django.db.models.functions import Floor

from .models import Categoria, Marca


# Opciones de orden: clave que viaja en la URL -> (texto visible, campo del ORM).
# El "-" delante del campo significa orden descendente (DESC en SQL).
ORDENES = {
    'recientes': ('Más recientes', '-fecha_creacion'),
    'precio_asc': ('Precio: menor a mayor', 'precio_final_db'),
    'precio_desc': ('Precio: mayor a menor', '-precio_final_db'),
    'nombre': ('Nombre (A-Z)', 'nombre'),
    'stock': ('Mayor stock', '-stock'),
}


class FiltroProductosForm(forms.Form):
    """
    Formulario de filtros. Es un forms.Form (no ModelForm) porque NO guarda
    nada en la base de datos: solo valida criterios de búsqueda.
    Todos los campos son opcionales (required=False): si vienen vacíos,
    simplemente no se aplica ese filtro.
    """

    q = forms.CharField(
        required=False,
        max_length=100,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre, descripción o marca...',
            'type': 'search',
        }),
    )

    # ModelChoiceField: las opciones salen de la tabla productos_categoria.
    # to_field_name='slug' hace que la URL use ?categoria=audio en vez de ?categoria=4.
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        to_field_name='slug',
        required=False,
        empty_label="Todas las categorías",
        label="Categoría",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    marca = forms.ModelChoiceField(
        queryset=Marca.objects.all(),
        required=False,
        empty_label="Todas las marcas",
        label="Marca",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    # min_value=0: rechaza precios negativos escritos a mano en la URL.
    precio_min = forms.IntegerField(
        required=False,
        min_value=0,
        label="Precio mínimo",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mín $', 'step': 1000}),
    )
    precio_max = forms.IntegerField(
        required=False,
        min_value=0,
        label="Precio máximo",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Máx $', 'step': 1000}),
    )

    disponibles = forms.BooleanField(
        required=False,
        label="Solo con stock",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    ofertas = forms.BooleanField(
        required=False,
        label="Solo ofertas",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    orden = forms.ChoiceField(
        required=False,
        choices=[(clave, texto) for clave, (texto, _) in ORDENES.items()],
        label="Ordenar por",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def clean(self):
        """Validación cruzada: el precio mínimo no puede ser mayor que el máximo."""
        datos = super().clean()
        minimo, maximo = datos.get('precio_min'), datos.get('precio_max')
        if minimo is not None and maximo is not None and minimo > maximo:
            self.add_error('precio_max', "El precio máximo debe ser mayor o igual al mínimo.")
        return datos

    def datos_validos(self):
        """
        Devuelve solo los filtros que pasaron la validación.
        - Sin parámetros en la URL: {} (se listan todos los productos).
        - Con un campo inválido (ej. ?precio_min=abc): ese campo se ignora,
          los demás filtros sí se aplican, y el error se muestra en pantalla.
        """
        if not self.is_bound:
            return {}
        self.is_valid()  # llena self.cleaned_data con los campos correctos
        return self.cleaned_data

    def hay_filtros(self):
        """True si el usuario aplicó al menos un filtro (para mostrar 'Limpiar filtros')."""
        if not self.is_bound:
            return False
        return any(self.data.get(campo) for campo in self.fields if campo != 'orden')


def anotar_precio_final(queryset):
    """
    Agrega a cada producto una columna CALCULADA por MySQL: precio_final_db.

    precio_final es una @property de Python, y MySQL no la conoce, así que no
    se puede filtrar ni ordenar por ella directamente. Con annotate() se le
    pide a MySQL que calcule el mismo valor dentro del SELECT:

        CASE WHEN oferta AND descuento > 0
             THEN precio - FLOOR(precio * descuento / 100)
             ELSE precio
        END AS precio_final_db

    FLOOR (redondear hacia abajo) replica el int() que usa la propiedad
    Producto.ahorro, para que el filtro coincida con el precio que se muestra.
    """
    return queryset.annotate(
        precio_final_db=Case(
            When(
                oferta=True,
                descuento__gt=0,
                then=F('precio') - Floor(F('precio') * F('descuento') / 100),
            ),
            default=F('precio'),
            output_field=IntegerField(),
        )
    )


def aplicar_filtros(queryset, datos):
    """
    Aplica al queryset solo los filtros que llegaron VÁLIDOS en "datos"
    (form.cleaned_data). Cada filtro agrega una condición al WHERE.

    Los QuerySets de Django son "perezosos": encadenar .filter() no consulta
    MySQL todavía; la consulta final se ejecuta una sola vez al recorrer
    los productos en la plantilla.
    """
    queryset = anotar_precio_final(queryset)

    # 1) Búsqueda de texto con Q objects (permiten combinar condiciones con OR "|").
    #    Cada palabra debe aparecer en el nombre, la descripción, la marca o la
    #    categoría. Las palabras se combinan con AND (filter encadenado):
    #    "teclado inalámbrico" -> productos que contengan AMBAS palabras.
    #    icontains = LIKE '%palabra%' sin distinguir mayúsculas; con la collation
    #    utf8mb4_unicode_ci de MySQL tampoco distingue tildes (periferico = periférico).
    texto = (datos.get('q') or '').strip()
    for palabra in texto.split():
        queryset = queryset.filter(
            Q(nombre__icontains=palabra)
            | Q(descripcion__icontains=palabra)
            | Q(marca__nombre__icontains=palabra)
            | Q(categoria__nombre__icontains=palabra)
        )

    # 2) Filtros por relación (ForeignKey) -> WHERE categoria_id = ... / marca_id = ...
    if datos.get('categoria'):
        queryset = queryset.filter(categoria=datos['categoria'])
    if datos.get('marca'):
        queryset = queryset.filter(marca=datos['marca'])

    # 3) Rango de precios sobre el precio FINAL (con descuento).
    #    __gte = mayor o igual (>=), __lte = menor o igual (<=).
    if datos.get('precio_min') is not None:
        queryset = queryset.filter(precio_final_db__gte=datos['precio_min'])
    if datos.get('precio_max') is not None:
        queryset = queryset.filter(precio_final_db__lte=datos['precio_max'])

    # 4) Disponibilidad con EXCLUSIÓN: exclude() genera WHERE NOT (stock = 0).
    if datos.get('disponibles'):
        queryset = queryset.exclude(stock=0)

    # 5) Ofertas: múltiples condiciones en un mismo filter() se unen con AND.
    if datos.get('ofertas'):
        queryset = queryset.filter(oferta=True, descuento__gt=0)

    # 6) Ordenamiento -> ORDER BY. Si no viene o es inválido, más recientes primero.
    _, campo_orden = ORDENES.get(datos.get('orden') or 'recientes', ORDENES['recientes'])
    return queryset.order_by(campo_orden, '-id')
