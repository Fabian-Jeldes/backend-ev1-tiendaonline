"""
=====================================================================
 usuarios/forms.py — Formulario de inicio de sesión
=====================================================================

LoginForm hereda de AuthenticationForm, el formulario oficial de Django.
No reimplementamos la verificación de contraseña: Django ya la hace de
forma segura (compara contra el hash PBKDF2 guardado en auth_user, nunca
contra texto plano). Aquí solo se cambia el aspecto (clases Bootstrap)
y los textos.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Tu nombre de usuario',
            'autofocus': True,
            'autocomplete': 'username',
        }),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,  # no se recortan espacios: forman parte de la contraseña
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Tu contraseña',
            'autocomplete': 'current-password',
        }),
    )

    # Mensaje genérico a propósito: no revela si lo incorrecto fue el usuario
    # o la contraseña, para no ayudar a un atacante a adivinar usuarios válidos.
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': "Usuario o contraseña incorrectos. Ten en cuenta que ambos distinguen mayúsculas.",
        'inactive': "Esta cuenta está desactivada.",
    }
