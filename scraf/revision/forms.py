from django.forms import *
from django import forms

from users.models import Personal
from revision.models import Revision, Revision_Activo

class R_Revision(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # Extraer el usuario actual de los kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        
        # Excluir al usuario actual del campo revisores
        if self.user and hasattr(self.user, 'personal_perfil'):
            # Filtrar el queryset para excluir el perfil del usuario actual
            self.fields['revisores'].queryset = Personal.objects.exclude(
                user=self.user
            )
    
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
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold border border-info'
            form.field.widget.attrs['autocomplete'] = 'off'
        
        # Personalizar específicamente el campo revisores
        self.fields['revisores'].widget.attrs.update({
            'class': 'form-select form-select-sm font-weight-bold border border-info',
            'size': '15'  # Mostrar 5 opciones a la vez
        })
        self.fields['revisores'].help_text = 'Mantén Ctrl (Cmd en Mac) presionado para seleccionar múltiples opciones'
        
        # Excluir usuario actual
        if self.user and hasattr(self.user, 'personal_perfil'):
            self.fields['revisores'].queryset = Personal.objects.exclude(
                user=self.user
            )
    
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
        
        # Configurar específicamente el campo estado como switch
        self.fields['estado'].widget.attrs['class'] = 'form-check-input'
        self.fields['estado'].widget.attrs['role'] = 'switch'
        
    class Meta:
        model = Revision_Activo
        fields = ['estado','observacion']
        labels = {
            'estado': '¿Requiere una segunda revisión?',
            'observacion': 'OBSERVACIÓN DE LA REVISIÓN'
        }
        widgets = {
            'estado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
