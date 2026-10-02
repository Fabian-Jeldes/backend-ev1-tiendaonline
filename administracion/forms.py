import re
from django import forms
from productos.models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'categoria',
            'precio',
            'stock',
            'oferta',
            'descuento',
            'imagen',
            'descripcion',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: Teclado Mecánico RGB Pro',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select form-select-lg',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1000',
                'min': '1',
                'placeholder': 'Ej: 99990',
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Ej: 10',
            }),
            'oferta': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'oferta',
                'onchange': 'toggleDescuento()',
            }),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'descuento',
                'min': '0',
                'max': '90',
                'placeholder': 'Ej: 15',
            }),
            'imagen': forms.URLInput(attrs={
                'class': 'form-control',
                'id': 'imagen',
                'placeholder': 'https://images.unsplash.com/...',
                'oninput': 'actualizarPreview()',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Especificaciones técnicas, características y detalles del producto...',
            }),
        }

    # =========================================================================
    # CRITERIO 2.1.4: VALIDACIONES PERSONALIZADAS POR CADA CAMPO DEL FORMULARIO
    # =========================================================================

    def clean_nombre(self):
        """Validación personalizada: longitud mínima, caracteres permitidos y seguridad."""
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre del producto debe contener al menos 3 caracteres.")
        if len(nombre) > 150:
            raise forms.ValidationError("El nombre del producto no puede exceder los 150 caracteres.")
        if nombre.isdigit():
            raise forms.ValidationError("El nombre no puede estar compuesto exclusivamente por números.")
        # Validación de seguridad: evitar etiquetas HTML o caracteres maliciosos
        if any(char in nombre for char in ['<', '>', '{', '}', ';', '$']):
            raise forms.ValidationError("Por seguridad, el nombre contiene caracteres no permitidos (<, >, {, }, ;, $).")
        return nombre

    def clean_categoria(self):
        """Validación personalizada: debe pertenecer a las categorías oficiales."""
        categoria = self.cleaned_data.get('categoria', '').strip()
        categorias_validas = [c[0] for c in Producto.CATEGORIAS]
        if categoria not in categorias_validas:
            raise forms.ValidationError(f"La categoría '{categoria}' no es válida. Elige una de la lista autorizada.")
        return categoria

    def clean_precio(self):
        """Validación personalizada: precio positivo y límites comerciales en CLP."""
        precio = self.cleaned_data.get('precio')
        if precio is None or precio <= 0:
            raise forms.ValidationError("El precio debe ser un valor entero positivo mayor a $0 CLP.")
        if precio < 500:
            raise forms.ValidationError("El precio mínimo permitido para cualquier artículo es de $500 CLP.")
        if precio > 50000000:
            raise forms.ValidationError("El precio excede el límite máximo comercial permitido ($50.000.000 CLP).")
        return precio

    def clean_stock(self):
        """Validación personalizada: stock no negativo y límite físico."""
        stock = self.cleaned_data.get('stock')
        if stock is None or stock < 0:
            raise forms.ValidationError("El stock disponible no puede ser un número negativo.")
        if stock > 10000:
            raise forms.ValidationError("El stock inicial no puede exceder las 10.000 unidades en inventario.")
        return stock

    def clean_descuento(self):
        """Validación personalizada: porcentaje entre 0 y 90%."""
        descuento = self.cleaned_data.get('descuento', 0)
        if descuento is None or descuento < 0:
            raise forms.ValidationError("El porcentaje de descuento no puede ser negativo.")
        if descuento > 90:
            raise forms.ValidationError("El porcentaje de descuento máximo permitido es del 90%.")
        return descuento

    def clean_imagen(self):
        """Validación personalizada: protocolo HTTP/HTTPS y formato de enlace."""
        imagen = self.cleaned_data.get('imagen', '').strip()
        if not imagen:
            raise forms.ValidationError("Debes proporcionar una URL válida para la imagen del producto.")
        if not (imagen.startswith('http://') or imagen.startswith('https://')):
            raise forms.ValidationError("La URL de la imagen debe comenzar con 'http://' o 'https://'.")
        if len(imagen) > 500:
            raise forms.ValidationError("La URL de la imagen es demasiado larga (máximo 500 caracteres).")
        return imagen

    def clean_descripcion(self):
        """Validación personalizada: descripción sustancial y segura."""
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        if len(descripcion) < 10:
            raise forms.ValidationError("La descripción debe tener al menos 10 caracteres con información técnica.")
        if any(char in descripcion for char in ['<script', '</script', 'javascript:']):
            raise forms.ValidationError("Por seguridad, no se admiten etiquetas de script en la descripción.")
        return descripcion

    def clean(self):
        """Validación cruzada entre campos: consistencia entre oferta y porcentaje."""
        cleaned_data = super().clean()
        oferta = cleaned_data.get('oferta')
        descuento = cleaned_data.get('descuento', 0)

        if oferta and (descuento is None or descuento <= 0):
            self.add_error('descuento', "Si activas la casilla de 'Oferta', debes ingresar un descuento mayor al 0%.")
        elif not oferta and descuento and descuento > 0:
            # Si no está en oferta, aseguramos que el descuento quede en 0
            cleaned_data['descuento'] = 0

        return cleaned_data
