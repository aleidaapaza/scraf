from django.forms import *
from django import forms

from revision.models import Revision, Revision_Activo

class R_Revision(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Revision
        fields = '__all__'
        exclude = ['slug', 'fecha_registro', 'estado', 'encargado', 'fechaHora_inicio', 'fechaHora_finalizacion']
        labels = {
            'motivo' : 'MOTIVO DE LA REVISION',
            'nombre' : 'TITULO DE LA REVISION',
            'descripcion' : 'DESCRIPCION DE LA REVISION',
            'revisores' : 'COMISION DE APOYO',
        }

class A_Revision_P(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Revision
        fields = ['revisores']
        labels = {
            'revisores' : 'COMISION DE APOYO',
        }

class A_Revision_S(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Revision
        fields = '__all__'
        exclude = ['slug', 'fecha_registro', 'estado', 'encargado', 'fechaHora_inicio', 'fechaHora_finalizacion']
        labels = {
            'motivo' : 'MOTIVO DE LA REVISION',
            'nombre' : 'TITULO DE LA REVISION',
            'descripcion' : 'DESCRIPCION DE LA REVISION',
            'revisores' : 'COMISION DE APOYO',
        }

class R_Revision_ACtivo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
    class Meta:
        model = Revision_Activo
        fields = ['observacion']
        labels ={
            'observacion' : 'OBSERVACION DE LA REVISION'
        }
