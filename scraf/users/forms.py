from django.forms import *
from django import forms
from users.models import Personal, User, Persona

class R_Persona(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Persona
        fields = '__all__'
        labels = {
            'nombre' : 'NOMBRE(S)',
            'apellido' : 'APELLIDO(S)',
            'cargo' : 'CARGO',
            'contacto' : 'CONTACTO',
            'carnet' : 'CARNET DE IDENTIDAD',
            'rubrica' : 'MOSCA',
        }

class R_User(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['is_encargado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
        self.fields['is_revisor'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
        self.fields['g_personal'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
        self.fields['g_Activos'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
        self.fields['v_Activos'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = User
        fields = ['username', 'is_encargado', 'is_revisor', 'g_personal', 'g_Activos', 'v_Activos']
        labels = {
            'username' : 'Nombre de usuario',
            'is_encargado' : '¿Habilitar como Encargado de Revision?',
            'is_revisor' : '¿Habilitar como Apoyo de Revision?',
            'g_personal' : 'Gestion de Personal ',
            'g_Activos' : 'Gestion de Activos Fijos',
            'v_Activos' : 'Solo Visualiza los Activos Fijos',
        }
        help_texts = {
            'g_personal' : 'Registra, modifica y Visualiza los datos del personal',
            'g_Activos' : 'Registra, modifica y Visualiza los datos de los activos fijos',
            'v_Activos' : 'Solo Visualiza los datos de los activos fijos'
        }
        

class A_Personal(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Personal
        exclude = '__all__'

class A_User(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-check font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['username'].widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
        self.fields['username'].widget.attrs['readonly'] = True
    
    class Meta:
        model = User
        fields = ['username', 'is_active', 'is_personal', 'is_encargado', 'is_revisor', 
                 'g_personal', 'g_mantenimiento', 'g_Activos', 'v_Activos']  # ✅ AGREGADO g_mantenimiento
        labels = {
            'username' : 'Nombre de usuario',
            'is_active' : '¿Usuario Activo?',
            'is_personal' : '¿Es Personal de la Institucion?',
            'is_encargado' : '¿Habilitar como Encargado de Revision?',
            'is_revisor' : '¿Habilitar como Apoyo de Revision?',
            'g_personal' : 'Gestion de Personal ',
            'g_mantenimiento' : 'Gestion de Mantenimiento',  # ✅ AGREGADO
            'g_Activos' : 'Gestion de Activos Fijos',
            'v_Activos' : 'Solo Visualiza los Activos Fijos',
        }
        help_texts = {
            'g_personal' : 'Registra, modifica y Visualiza los datos del personal',
            'g_mantenimiento' : 'Puede poner activos en mantenimiento',  # ✅ AGREGADO
            'g_Activos' : 'Registra, modifica y Visualiza los datos de los activos fijos',
            'v_Activos' : 'Solo Visualiza los datos de los activos fijos'
        }

class A_Persona(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['nombre'].widget.attrs['readonly'] = True
        self.fields['apellido'].widget.attrs['readonly'] = True
        self.fields['carnet'].widget.attrs['readonly'] = True
        self.fields['rubrica'].widget.attrs['readonly'] = True
    
    class Meta:
        model = Persona
        fields = '__all__'
        labels = {
            'nombre' : 'NOMBRE(S)',
            'apellido' : 'APELLIDO(S)',
            'cargo' : 'CARGO',
            'contacto' : 'CONTACTO',
            'carnet' : 'CARNET DE IDENTIDAD',
            'rubrica' : 'MOSCA',
        }