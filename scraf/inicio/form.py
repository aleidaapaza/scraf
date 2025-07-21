from django.forms import *
from django import forms

class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'

    username = forms.CharField(max_length=150, label='Nombre de Usuario', widget=forms.TextInput(attrs={'placeholder': 'Ingrese su nombre de usuario'}))
    password = forms.CharField(max_length=255, label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}))
