from django import forms
from django.contrib.auth import authenticate
from .models import (
    Usuario, PCArmada, Teclado, Monitor, Mouse, Audifonos, Proveedor, Pedido
)


class FormularioRegistroUsuario(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput, label='Contraseña')
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput, label='Confirmar contraseña')

    class Meta:
        model = Usuario
        fields = ['nombre', 'usuario', 'correo', 'ciudad', 'calle', 'colonia', 'numero_casa']

    def clean(self):
        datos = super().clean()
        contraseña = datos.get('contraseña')
        confirmar = datos.get('confirmar_contraseña')
        if contraseña and confirmar and contraseña != confirmar:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.set_password(self.cleaned_data['contraseña'])
        if commit:
            usuario.save()
        return usuario


class FormularioAcceso(forms.Form):
    usuario = forms.CharField(label='Usuario')
    contraseña = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

    def autenticar(self):
        usuario = self.cleaned_data.get('usuario')
        contraseña = self.cleaned_data.get('contraseña')
        return authenticate(username=usuario, password=contraseña)


class FormularioPerfilUsuario(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'ciudad', 'calle', 'colonia', 'numero_casa']


class FormularioPCArmada(forms.ModelForm):
    class Meta:
        model = PCArmada
        fields = ['foto', 'nombre', 'precio', 'categoria']


class FormularioTeclado(forms.ModelForm):
    class Meta:
        model = Teclado
        fields = ['foto', 'nombre', 'precio', 'categoria']


class FormularioMonitor(forms.ModelForm):
    class Meta:
        model = Monitor
        fields = ['foto', 'nombre', 'tamaño', 'precio', 'categoria']


class FormularioMouse(forms.ModelForm):
    class Meta:
        model = Mouse
        fields = ['foto', 'nombre', 'precio', 'categoria', 'color']


class FormularioAudifonos(forms.ModelForm):
    class Meta:
        model = Audifonos
        fields = ['foto', 'nombre', 'color', 'precio', 'categoria']


class FormularioProveedor(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['id_producto', 'nombre', 'precio']


class FormularioCheckout(forms.Form):
    METODOS = [
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('paypal', 'PayPal'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    metodo_pago = forms.ChoiceField(choices=METODOS, label='Método de pago')
    calle_envio = forms.CharField(max_length=120, label='Calle de envío')
    colonia_envio = forms.CharField(max_length=120, label='Colonia')
    ciudad_envio = forms.CharField(max_length=120, label='Ciudad')
    numero_envio = forms.CharField(max_length=20, label='Número de casa')
    notas = forms.CharField(widget=forms.Textarea, required=False, label='Notas para el repartidor')


class FormularioBusqueda(forms.Form):
    busqueda = forms.CharField(max_length=100, required=False, label='Buscar')


class FormularioEstadoPedido(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado', 'fecha_entrega']