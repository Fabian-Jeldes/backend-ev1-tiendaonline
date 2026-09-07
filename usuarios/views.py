from django.shortcuts import render

def registro(request):
    """
    Vista para gestionar el registro de nuevos usuarios en la tienda.
    Demuestra manejo de formularios, estructuras de decisión (POST vs GET)
    y paso de mensajes de confirmación a la interfaz.
    """
    mensaje_exito = None
    datos_usuario = None

    # Estructura de decisión: verificamos si el usuario envió el formulario por POST
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        ciudad = request.POST.get('ciudad', '').strip()

        # Operadores lógicos: validamos que los campos obligatorios no vengan vacíos
        if nombre and email:
            mensaje_exito = f"¡Bienvenido/a {nombre}! Tu cuenta ha sido registrada con éxito."
            datos_usuario = {
                'nombre': nombre,
                'email': email,
                'ciudad': ciudad or 'Santiago',
            }

    contexto = {
        'titulo': 'Registro de Clientes',
        'mensaje_exito': mensaje_exito,
        'datos_usuario': datos_usuario,
    }
    return render(request, 'usuarios/registro.html', contexto)


def perfil(request):
    """
    Vista de perfil de cliente con datos estructurados en un diccionario de Python.
    """
    # Diccionario con datos de simulación del perfil de usuario
    perfil_cliente = {
        'nombre_completo': 'Fabián Pérez',
        'rut': '20.123.456-7',
        'email': 'fabian.perez@inacapmail.cl',
        'telefono': '+56 9 8765 4321',
        'direccion': 'Av. Apoquindo 4500, Las Condes',
        'ciudad': 'Santiago',
        'categoria_cliente': 'Cliente VIP',
        'puntos_acumulados': 1450,
        'compras_realizadas': 4,
    }

    contexto = {
        'titulo': 'Perfil de Usuario',
        'perfil': perfil_cliente,
    }
    return render(request, 'usuarios/perfil.html', contexto)
