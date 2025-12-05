from decimal import Decimal
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    FormularioRegistroUsuario,
    FormularioAcceso,
    FormularioPerfilUsuario,
    FormularioPCArmada,
    FormularioTeclado,
    FormularioMonitor,
    FormularioMouse,
    FormularioAudifonos,
    FormularioProveedor,
    FormularioCheckout,
    FormularioBusqueda,
    FormularioEstadoPedido,
)
from .models import (
    Usuario,
    PCArmada,
    Teclado,
    Monitor,
    Mouse,
    Audifonos,
    Proveedor,
    Pedido,
)

MAPEO_PRODUCTOS = {
    'pc': {
        'modelo': PCArmada,
        'formulario': FormularioPCArmada,
        'nombre': 'PC Armadas'
    },
    'teclado': {
        'modelo': Teclado,
        'formulario': FormularioTeclado,
        'nombre': 'Teclados'
    },
    'monitor': {
        'modelo': Monitor,
        'formulario': FormularioMonitor,
        'nombre': 'Monitores'
    },
    'mouse': {
        'modelo': Mouse,
        'formulario': FormularioMouse,
        'nombre': 'Mouses'
    },
    'audifonos': {
        'modelo': Audifonos,
        'formulario': FormularioAudifonos,
        'nombre': 'Audífonos'
    },
}


def obtener_carrito(request):
    return request.session.get('carrito', {})


def guardar_carrito(request, carrito):
    request.session['carrito'] = carrito
    request.session.modified = True


def calcular_totales_carrito(carrito):
    subtotal = Decimal('0.00')
    for datos in carrito.values():
        subtotal += Decimal(datos['precio']) * datos['cantidad']
    impuestos = subtotal * Decimal('0.16')
    total = subtotal + impuestos
    return subtotal, impuestos, total


def construir_tarjeta(producto, tipo):
    return {
        'tipo': tipo,
        'objeto': producto,
        'pk': producto.pk,
        'nombre_tipo': MAPEO_PRODUCTOS[tipo]['nombre'],
    }


def index(request):
    productos_destacados = []
    for clave, datos in MAPEO_PRODUCTOS.items():
        objetos = datos['modelo'].objects.all()[:3]
        for objeto in objetos:
            productos_destacados.append(construir_tarjeta(objeto, clave))
    contexto = {
        'productos_destacados': productos_destacados,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/index.html', contexto)


def lista_productos(request):
    productos = []
    termino = request.GET.get('busqueda', '')
    for clave, datos in MAPEO_PRODUCTOS.items():
        queryset = datos['modelo'].objects.all()
        if termino:
            queryset = queryset.filter(
                Q(nombre__icontains=termino) |
                Q(categoria__icontains=termino)
            )
        for objeto in queryset:
            productos.append(construir_tarjeta(objeto, clave))
    contexto = {
        'productos': productos,
        'termino': termino,
        'formulario_busqueda': FormularioBusqueda(initial={'busqueda': termino}),
    }
    return render(request, 'usuario/productos.html', contexto)


def productos_por_tipo(request, tipo):
    if tipo not in MAPEO_PRODUCTOS:
        messages.error(request, 'Tipo de producto no encontrado.')
        return redirect('lista_productos')
    modelo = MAPEO_PRODUCTOS[tipo]['modelo']
    objetos = modelo.objects.all()
    tarjetas = [construir_tarjeta(objeto, tipo) for objeto in objetos]
    contexto = {
        'productos': tarjetas,
        'titulo_categoria': MAPEO_PRODUCTOS[tipo]['nombre'],
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/productos.html', contexto)


def detalle_producto(request, tipo, pk):
    if tipo not in MAPEO_PRODUCTOS:
        messages.error(request, 'Producto no disponible.')
        return redirect('lista_productos')
    modelo = MAPEO_PRODUCTOS[tipo]['modelo']
    producto = get_object_or_404(modelo, pk=pk)
    contexto = {
        'producto': producto,
        'tipo': tipo,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/detalle_producto.html', contexto)


def agregar_al_carrito(request, tipo, pk):
    if tipo not in MAPEO_PRODUCTOS:
        messages.error(request, 'No se pudo agregar el producto.')
        return redirect('lista_productos')
    modelo = MAPEO_PRODUCTOS[tipo]['modelo']
    producto = get_object_or_404(modelo, pk=pk)
    carrito = obtener_carrito(request)
    clave = f'{tipo}-{pk}'
    if clave not in carrito:
        carrito[clave] = {
            'tipo': tipo,
            'id': pk,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': 1,
            'categoria': getattr(producto, 'categoria', ''),
            'imagen': producto.foto.url if producto.foto else '',
        }
    else:
        carrito[clave]['cantidad'] += 1
    guardar_carrito(request, carrito)
    messages.success(request, 'Producto agregado al carrito.')
    return redirect('ver_carrito')


def ver_carrito(request):
    carrito = obtener_carrito(request)
    subtotal, impuestos, total = calcular_totales_carrito(carrito)
    contexto = {
        'carrito': carrito,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/carrito.html', contexto)


def actualizar_cantidad_carrito(request, clave):
    carrito = obtener_carrito(request)
    if request.method == 'POST' and clave in carrito:
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            cantidad = 1
        if cantidad <= 0:
            carrito.pop(clave)
        else:
            carrito[clave]['cantidad'] = cantidad
        guardar_carrito(request, carrito)
        messages.success(request, 'Carrito actualizado.')
    return redirect('ver_carrito')


def eliminar_del_carrito(request, clave):
    carrito = obtener_carrito(request)
    if clave in carrito:
        carrito.pop(clave)
        guardar_carrito(request, carrito)
        messages.info(request, 'Producto eliminado del carrito.')
    return redirect('ver_carrito')


def vaciar_carrito(request):
    guardar_carrito(request, {})
    messages.info(request, 'Carrito vacío.')
    return redirect('ver_carrito')


@login_required
def checkout(request):
    carrito = obtener_carrito(request)
    if not carrito:
        messages.warning(request, 'El carrito está vacío.')
        return redirect('lista_productos')

    subtotal, impuestos, total = calcular_totales_carrito(carrito)

    inicial = {
        'calle_envio': request.user.calle,
        'colonia_envio': request.user.colonia,
        'ciudad_envio': request.user.ciudad,
        'numero_envio': request.user.numero_casa,
    }

    if request.method == 'POST':
        formulario = FormularioCheckout(request.POST)
        if formulario.is_valid():
            metodo_pago = formulario.cleaned_data['metodo_pago']
            direccion = (
                f"{formulario.cleaned_data['calle_envio']} #{formulario.cleaned_data['numero_envio']}, "
                f"{formulario.cleaned_data['colonia_envio']}, "
                f"{formulario.cleaned_data['ciudad_envio']}"
            )
            notas = formulario.cleaned_data.get('notas', '')
            resumen = []
            clave_productos = []
            for clave, datos in carrito.items():
                resumen.append(f"{datos['nombre']} x {datos['cantidad']} (${datos['precio']})")
                clave_productos.append(clave)

            detalles = (
                f"Método de pago: {metodo_pago}. "
                f"Dirección de envío: {direccion}. "
                f"Impuestos aplicados: 16%. "
                f"Notas: {notas}. "
                f"Productos: {' | '.join(resumen)}."
            )

            pedido = Pedido.objects.create(
                id_producto=",".join(clave_productos),
                usuario=request.user,
                detalles=detalles,
                precio=total,
                fecha_entrega=timezone.now() + timedelta(days=5),
                estado='Procesando'
            )
            guardar_carrito(request, {})
            messages.success(request, f'Pedido generado con éxito. Número de pedido #{pedido.id_pedido}.')
            return redirect('pedidos_usuario')
    else:
        formulario = FormularioCheckout(initial=inicial)

    contexto = {
        'carrito': carrito,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total,
        'formulario': formulario,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/checkout.html', contexto)


def registrar_usuario(request):
    if request.user.is_authenticated:
        return redirect('perfil_usuario')
    if request.method == 'POST':
        formulario = FormularioRegistroUsuario(request.POST, request.FILES)
        if formulario.is_valid():
            nuevo = formulario.save()
            login(request, nuevo)
            messages.success(request, 'Cuenta creada correctamente.')
            return redirect('index')
    else:
        formulario = FormularioRegistroUsuario()
    contexto = {
        'formulario': formulario,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/registro.html', contexto)


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('perfil_usuario')
    if request.method == 'POST':
        formulario = FormularioAcceso(request.POST)
        if formulario.is_valid():
            usuario_autenticado = formulario.autenticar()
            if usuario_autenticado:
                if not usuario_autenticado.es_activo:
                    messages.error(request, 'Tu cuenta está desactivada.')
                else:
                    login(request, usuario_autenticado)
                    messages.success(request, 'Sesión iniciada.')
                    if usuario_autenticado.es_admin:
                        return redirect('panel_admin')
                    return redirect('index')
            else:
                messages.error(request, 'Credenciales incorrectas.')
    else:
        formulario = FormularioAcceso()
    contexto = {
        'formulario': formulario,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/iniciar_sesion.html', contexto)


@login_required
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('index')


@login_required
def perfil_usuario(request):
    pedidos = request.user.pedidos.order_by('-fecha_pedido')
    contexto = {
        'usuario_actual': request.user,
        'pedidos': pedidos,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/perfil.html', contexto)


@login_required
def pedidos_usuario(request):
    pedidos = request.user.pedidos.order_by('-fecha_pedido')
    contexto = {
        'pedidos': pedidos,
        'formulario_busqueda': FormularioBusqueda(),
    }
    return render(request, 'usuario/perfil.html', contexto)


def buscar_productos(request):
    termino = request.GET.get('busqueda', '')
    return redirect(f'/productos/?busqueda={termino}')


def verificar_admin(usuario):
    return usuario.is_authenticated and usuario.es_admin


@login_required
def panel_admin(request):
    if not verificar_admin(request.user):
        messages.error(request, 'Acceso restringido.')
        return redirect('index')
    totales = {
        'pc': PCArmada.objects.count(),
        'teclado': Teclado.objects.count(),
        'monitor': Monitor.objects.count(),
        'mouse': Mouse.objects.count(),
        'audifonos': Audifonos.objects.count(),
        'proveedores': Proveedor.objects.count(),
        'pedidos': Pedido.objects.count(),
        'usuarios': Usuario.objects.count(),
    }
    contexto = {
        'totales': totales,
    }
    return render(request, 'admin/panel.html', contexto)


@login_required
def admin_lista_productos(request, tipo):
    if not verificar_admin(request.user):
        return redirect('index')
    if tipo not in MAPEO_PRODUCTOS:
        messages.error(request, 'Tipo de producto desconocido.')
        return redirect('panel_admin')
    modelo = MAPEO_PRODUCTOS[tipo]['modelo']
    objetos = modelo.objects.all()
    contexto = {
        'objetos': objetos,
        'tipo': tipo,
        'titulo': MAPEO_PRODUCTOS[tipo]['nombre'],
    }
    return render(request, 'admin/lista_productos.html', contexto)


@login_required
def admin_crear_producto(request, tipo):
    if not verificar_admin(request.user):
        return redirect('index')
    if tipo not in MAPEO_PRODUCTOS:
        messages.error(request, 'Tipo de producto desconocido.')
        return redirect('panel_admin')
    formulario_clase = MAPEO_PRODUCTOS[tipo]['formulario']
    if request.method == 'POST':
        formulario = formulario_clase(request.POST, request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Producto creado.')
            return redirect('admin_lista_productos', tipo=tipo)
    else:
        formulario = formulario_clase()
    contexto = {
        'formulario': formulario,
        'tipo': tipo,
        'titulo': f'Crear {MAPEO_PRODUCTOS[tipo]["nombre"]}',
    }
    return render(request, 'admin/formulario_producto.html', contexto)


@login_required
def admin_editar_producto(request, tipo, pk):
    if not verificar_admin(request.user):
        return redirect('index')
    if tipo not in MAPEO_PRODUCTOS:
        messages.error(request, 'Tipo de producto desconocido.')
        return redirect('panel_admin')
    modelo = MAPEO_PRODUCTOS[tipo]['modelo']
    objeto = get_object_or_404(modelo, pk=pk)
    formulario_clase = MAPEO_PRODUCTOS[tipo]['formulario']
    if request.method == 'POST':
        formulario = formulario_clase(request.POST, request.FILES, instance=objeto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('admin_lista_productos', tipo=tipo)
    else:
        formulario = formulario_clase(instance=objeto)
    contexto = {
        'formulario': formulario,
        'tipo': tipo,
        'titulo': f'Editar {MAPEO_PRODUCTOS[tipo]["nombre"]}',
    }
    return render(request, 'admin/formulario_producto.html', contexto)


@login_required
def admin_eliminar_producto(request, tipo, pk):
    if not verificar_admin(request.user):
        return redirect('index')
    if tipo not in MAPEO_PRODUCTOS:
        messages.error(request, 'Tipo de producto desconocido.')
        return redirect('panel_admin')
    modelo = MAPEO_PRODUCTOS[tipo]['modelo']
    objeto = get_object_or_404(modelo, pk=pk)
    objeto.delete()
    messages.info(request, 'Producto eliminado.')
    return redirect('admin_lista_productos', tipo=tipo)


@login_required
def admin_lista_proveedores(request):
    if not verificar_admin(request.user):
        return redirect('index')
    proveedores = Proveedor.objects.all()
    contexto = {
        'proveedores': proveedores,
    }
    return render(request, 'admin/lista_proveedores.html', contexto)


@login_required
def admin_crear_proveedor(request):
    if not verificar_admin(request.user):
        return redirect('index')
    if request.method == 'POST':
        formulario = FormularioProveedor(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Proveedor creado.')
            return redirect('admin_lista_proveedores')
    else:
        formulario = FormularioProveedor()
    contexto = {
        'formulario': formulario,
        'titulo': 'Crear proveedor',
    }
    return render(request, 'admin/formulario_proveedor.html', contexto)


@login_required
def admin_editar_proveedor(request, pk):
    if not verificar_admin(request.user):
        return redirect('index')
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        formulario = FormularioProveedor(request.POST, instance=proveedor)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Proveedor actualizado.')
            return redirect('admin_lista_proveedores')
    else:
        formulario = FormularioProveedor(instance=proveedor)
    contexto = {
        'formulario': formulario,
        'titulo': 'Editar proveedor',
    }
    return render(request, 'admin/formulario_proveedor.html', contexto)


@login_required
def admin_eliminar_proveedor(request, pk):
    if not verificar_admin(request.user):
        return redirect('index')
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.delete()
    messages.info(request, 'Proveedor eliminado.')
    return redirect('admin_lista_proveedores')


@login_required
def admin_lista_pedidos(request):
    if not verificar_admin(request.user):
        return redirect('index')
    pedidos = Pedido.objects.select_related('usuario').order_by('-fecha_pedido')
    contexto = {
        'pedidos': pedidos,
        'formulario_estado': FormularioEstadoPedido(),
    }
    return render(request, 'admin/lista_pedidos.html', contexto)


@login_required
def admin_actualizar_estado_pedido(request, pk):
    if not verificar_admin(request.user):
        return redirect('index')
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        formulario = FormularioEstadoPedido(request.POST, instance=pedido)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Estado del pedido actualizado.')
    return redirect('admin_lista_pedidos')


@login_required
def admin_detalle_usuario(request, pk):
    if not verificar_admin(request.user):
        return redirect('index')
    usuario_obj = get_object_or_404(Usuario, pk=pk)
    pedidos = usuario_obj.pedidos.order_by('-fecha_pedido')
    contexto = {
        'usuario_obj': usuario_obj,
        'pedidos': pedidos,
    }
    return render(request, 'admin/detalle_usuario.html', contexto)