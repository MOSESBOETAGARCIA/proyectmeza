from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, PCArmada, Teclado, Monitor, Mouse, Audifonos, Proveedor, Pedido
)


class UsuarioAdmin(UserAdmin):
    ordering = ['id_usuario']
    list_display = ['usuario', 'nombre', 'correo', 'es_admin', 'es_activo']
    list_filter = ['es_admin', 'es_activo']
    fieldsets = (
        (None, {'fields': ('usuario', 'password')}),
        ('Información personal', {'fields': ('nombre', 'correo', 'ciudad', 'calle', 'colonia', 'numero_casa')}),
        ('Permisos', {'fields': ('es_activo', 'es_admin', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('usuario', 'nombre', 'correo', 'password1', 'password2', 'es_admin', 'es_activo')
        }),
    )
    search_fields = ('usuario', 'correo', 'nombre')
    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(PCArmada)
admin.site.register(Teclado)
admin.site.register(Monitor)
admin.site.register(Mouse)
admin.site.register(Audifonos)
admin.site.register(Proveedor)
admin.site.register(Pedido)