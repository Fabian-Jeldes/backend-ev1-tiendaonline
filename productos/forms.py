import re
from django import forms
from .models import MensajeContacto

class ContactoForm(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'telefono', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Tu nombre y apellido',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'ejemplo@dominio.cl',
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': '+56 9 1234 5678',
            }),
            'asunto': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Motivo de tu consulta o requerimiento',
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escribe aquí tu consulta en detalle...',
            }),
        }

    # =========================================================================
    # VALIDACIONES PERSONALIZADAS POR CADA CAMPO
    # =========================================================================

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        if any(char in nombre for char in ['<', '>', '{', '}', ';', '$']):
            raise forms.ValidationError("El nombre contiene caracteres especiales no permitidos.")
        return nombre

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise forms.ValidationError("Ingresa una dirección de correo electrónico válida (ej: contacto@empresa.cl).")
        return email

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if telefono:
            telefono = telefono.strip()
            # Permitir dígitos, espacios, guiones y el signo +
            if not re.match(r'^\+?[0-9\s\-]{8,18}$', telefono):
                raise forms.ValidationError("Ingresa un número telefónico válido (ej: +56 9 1234 5678).")
        return telefono

    def clean_asunto(self):
        asunto = self.cleaned_data.get('asunto', '').strip()
        if len(asunto) < 4:
            raise forms.ValidationError("El asunto debe contener al menos 4 caracteres.")
        return asunto

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje', '').strip()
        if len(mensaje) < 10:
            raise forms.ValidationError("El mensaje debe contener al menos 10 caracteres explicativos.")
        return mensaje
