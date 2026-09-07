from django.urls import path
from . import views

urlpatterns = [
    # Ruta: /productos/ -> Muestra el catálogo con los 4 productos
    path('', views.catalogo, name='catalogo'),
    
    # Ruta: /productos/1/ -> Muestra el detalle del producto con ID 1
    # <int:id> captura el número en la URL y se lo pasa como parámetro a la función detalle_producto
    path('<int:id>/', views.detalle_producto, name='detalle_producto'),
]
