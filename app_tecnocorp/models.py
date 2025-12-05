from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class GestorUsuario(BaseUserManager):
    def create_user(self, usuario, nombre, correo, password=None, **extra):
        if not usuario:
            raise ValueError('El campo usuario es obligatorio')
        if not correo:
            raise ValueError('El campo correo es obligatorio')
        correo = self.normalize_email(correo)
        nuevo_usuario = self.model(
            usuario=usuario,
            nombre=nombre,
            correo=correo,
            **extra
        )
        nuevo_usuario.set_password(password)
        nuevo_usuario.save(using=self._db)
        return nuevo_usuario

    def create_superuser(self, usuario, nombre, correo, password=None, **extra):
        extra.setdefault('es_admin', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('es_activo', True)
        if extra.get('es_admin') is not True:
            raise ValueError('El superusuario debe tener es_admin=True.')
        if extra.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        return self.create_user(usuario, nombre, correo, password, **extra)

    # Opcional: mantén los nombres en español como alias si los usas en otro lugar
    def crear_usuario(self, usuario, nombre, correo, contraseña=None, **extra):
        return self.create_user(usuario, nombre, correo, contraseña, **extra)

    def crear_superusuario(self, usuario, nombre, correo, contraseña=None, **extra):
        return self.create_superuser(usuario, nombre, correo, contraseña, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    usuario = models.CharField(max_length=150, unique=True)
    correo = models.EmailField(unique=True)
    ciudad = models.CharField(max_length=120, blank=True)
    calle = models.CharField(max_length=120, blank=True)
    colonia = models.CharField(max_length=120, blank=True)
    numero_casa = models.CharField(max_length=20, blank=True)
    es_activo = models.BooleanField(default=True)
    es_admin = models.BooleanField(default=False)

    objects = GestorUsuario()

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = ['nombre', 'correo']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.nombre} ({self.usuario})'

    @property
    def is_staff(self):
        return self.es_admin

    def tiene_direccion(self):
        return all([self.calle, self.colonia, self.ciudad, self.numero_casa])


class PCArmada(models.Model):
    id_pc = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='productos/pc/', blank=True, null=True)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'PC Armado'
        verbose_name_plural = 'PC Armadas'

    def __str__(self):
        return self.nombre


class Teclado(models.Model):
    id_teclado = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='productos/teclados/', blank=True, null=True)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Teclado'
        verbose_name_plural = 'Teclados'

    def __str__(self):
        return self.nombre


class Monitor(models.Model):
    id_monitor = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='productos/monitores/', blank=True, null=True)
    nombre = models.CharField(max_length=200)
    tamaño = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Monitor'
        verbose_name_plural = 'Monitores'

    def __str__(self):
        return self.nombre


class Mouse(models.Model):
    id_mouse = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='productos/mouse/', blank=True, null=True)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)
    color = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Mouse'
        verbose_name_plural = 'Mouses'

    def __str__(self):
        return self.nombre


class Audifonos(models.Model):
    id_audifonos = models.AutoField(primary_key=True)
    foto = models.ImageField(upload_to='productos/audifonos/', blank=True, null=True)
    nombre = models.CharField(max_length=200)
    color = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Audífono'
        verbose_name_plural = 'Audífonos'

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    id_producto = models.CharField(max_length=120)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return f'{self.nombre} - {self.id_producto}'


class Pedido(models.Model):
    ESTADOS = [
        ('Procesando', 'Procesando'),
        ('En camino', 'En camino'),
        ('Entregado', 'Entregado'),
        ('Cancelado', 'Cancelado'),
    ]

    id_pedido = models.AutoField(primary_key=True)
    id_producto = models.CharField(max_length=150)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    detalles = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pedido = models.DateTimeField(default=timezone.now)
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='Procesando')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.id_pedido} - {self.usuario.usuario}'