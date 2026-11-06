"""
Migración de datos: crea el grupo (rol) "Editores de catálogo".

Un GRUPO en Django es un conjunto de permisos. Al asignar un usuario a un
grupo, hereda todos sus permisos. Este grupo sirve para demostrar el control
de acceso por roles:

    Permiso                     Superusuario   Editores de catálogo
    productos.view_producto          ✔                 ✔
    productos.add_producto           ✔                 ✔
    productos.change_producto        ✔                 ✔
    productos.delete_producto        ✔                 ✘  -> /eliminar/ responde 403

Para usarlo: /admin/ -> Usuarios -> (usuario) -> Grupos -> "Editores de catálogo".
"""

from django.contrib.auth.management import create_permissions
from django.db import migrations

NOMBRE_GRUPO = 'Editores de catálogo'
PERMISOS = ['view_producto', 'add_producto', 'change_producto']


def crear_grupo(apps, schema_editor):
    # Django crea los permisos automáticamente DESPUÉS de todas las migraciones
    # (señal post_migrate). En una base nueva todavía no existirían aquí, así que
    # se fuerzan a crear antes de asignarlos.
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    grupo, _ = Group.objects.get_or_create(name=NOMBRE_GRUPO)
    grupo.permissions.set(
        Permission.objects.filter(content_type__app_label='productos', codename__in=PERMISOS)
    )


def borrar_grupo(apps, schema_editor):
    apps.get_model('auth', 'Group').objects.filter(name=NOMBRE_GRUPO).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('productos', '0004_producto_categoria_fk'),
    ]

    operations = [
        migrations.RunPython(crear_grupo, borrar_grupo),
    ]
