from django.forms import *
from django import forms

from activos.models import Activo, Activo_responsable

class R_Activo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Activo
        fields = '__all__'
        labels = {
            'codigo' : 'CODIGO DEL ACTIVO',
            'descActivo' : 'DESCRIPCION DEL ACTIVO',
            'descripcion' : 'DESCRIPCION',
        }

class R_Activo_responsable(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Activo_responsable
        fields = '__all__'
        exclude = ['slug', 'activo']
        labels = {
            'responsable' : 'RESPONSABLE DEL ACTIVO',
            'piso_ubicacion' : 'PISO DONDE SE ENCUENTRA UBICADO EL ACTIVO',
            'oficina_ubicacion' : 'OFICINA DONDE SE ENCUENTRA UBICADO EL ACTIVO',
            'estado' : 'ESTADO DEL ACTIVO',
        }
        
class A_Activo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['codigo'].disabled = True
        self.fields['descActivo'].disabled = True
        self.fields['descripcion'].disabled = True
    
    class Meta:
        model = Activo
        fields = '__all__'
        labels = {
            'codigo' : 'CODIGO DEL ACTIVO',
            'descActivo' : 'DESCRIPCION DEL ACTIVO',
            'descripcion' : 'DESCRIPCION',
        }

class A_Activo_responsable(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-select font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        self.fields['estado'].widget.attrs['disabled'] = True
        self.fields['responsable'].widget.attrs['disabled'] = True
    
    class Meta:
        model = Activo_responsable
        fields = '__all__'
        exclude = ['slug', 'activo']
        labels = {
            'responsable' : 'RESPONSABLE ACTUAL DEL ACTIVO',
            'piso_ubicacion' : 'PISO DONDE SE ENCUENTRA UBICADO EL ACTIVO',
            'oficina_ubicacion' : 'OFICINA DONDE SE ENCUENTRA UBICADO EL ACTIVO',
            'estado' : 'ESTADO ACTUAL DEL ACTIVO',
        }