from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/<str:tipo>/', views.productos_por_tipo, name='productos_por_tipo'),
    path('producto/<str:tipo>/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/agregar/<str:tipo>/<int:pk>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/<str:clave>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('carrito/eliminar/<str:clave>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('registro/', views.registrar_usuario, name='registro'),
    path('login/', views.iniciar_sesion, name='iniciar_sesion'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    path('pedidos/', views.pedidos_usuario, name='pedidos_usuario'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    # Panel administrador
    path('admin-tecnocorp/', views.panel_admin, name='panel_admin'),
    path('admin-tecnocorp/productos/<str:tipo>/', views.admin_lista_productos, name='admin_lista_productos'),
    path('admin-tecnocorp/productos/<str:tipo>/nuevo/', views.admin_crear_producto, name='admin_crear_producto'),
    path('admin-tecnocorp/productos/<str:tipo>/<int:pk>/editar/', views.admin_editar_producto, name='admin_editar_producto'),
    path('admin-tecnocorp/productos/<str:tipo>/<int:pk>/eliminar/', views.admin_eliminar_producto, name='admin_eliminar_producto'),
    path('admin-tecnocorp/proveedores/', views.admin_lista_proveedores, name='admin_lista_proveedores'),
    path('admin-tecnocorp/proveedores/nuevo/', views.admin_crear_proveedor, name='admin_crear_proveedor'),
    path('admin-tecnocorp/proveedores/<int:pk>/editar/', views.admin_editar_proveedor, name='admin_editar_proveedor'),
    path('admin-tecnocorp/proveedores/<int:pk>/eliminar/', views.admin_eliminar_proveedor, name='admin_eliminar_proveedor'),
    path('admin-tecnocorp/pedidos/', views.admin_lista_pedidos, name='admin_lista_pedidos'),
    path('admin-tecnocorp/pedidos/<int:pk>/estado/', views.admin_actualizar_estado_pedido, name='admin_actualizar_estado_pedido'),
    path('admin-tecnocorp/usuarios/<int:pk>/', views.admin_detalle_usuario, name='admin_detalle_usuario'),
]