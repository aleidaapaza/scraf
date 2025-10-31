from django_select2.forms import ModelSelect2Widget
from django.forms import *
from django import forms

from activos.models import Activo, GrupoContable, AuxiliarContable, MantenimientoActivo
from designacion.models import Activo_responsable

class R_Activo(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold'
            form.field.widget.attrs['autocomplete'] = 'off'
        #self.fields['estado'].widget.attrs['class'] = 'form-check font-weight-bold border border-info'
    
    class Meta:
        model = Activo
        fields = '__all__'
        exclude = ['estadoDesignacion', 'mantenimiento']
        labels = {
            'codigo' : 'CODIGO DEL ACTIVO',
            'descActivo' : 'DESCRIPCION DEL ACTIVO',
            'descripcion' : 'DESCRIPCION',
        }

class R_Activo_responsable(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold'
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
        
class A_Activo_responsable(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-select font-weight-bold'
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
class R_GrupoContable(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold'
            form.field.widget.attrs['autocomplete'] = 'off'
    
    class Meta:
        model = GrupoContable
        fields = '__all__'
        labels = {
            'nombre' : 'NOMBRE DEL GRUPO CONTABLE',
        }

class R_auxiliar(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control form-control-sm font-weight-bold'
            form.field.widget.attrs['autocomplete'] = 'off'
    
    class Meta:
        model = GrupoContable
        fields = '__all__'
        exclude = ['grupocontable']
        labels = {
            'nombre' : 'NOMBRE DEL AUXILIAR CONTABLE',
        }
        
class CargaCSVForm(forms.Form):
    archivo = forms.FileField(
        label="Archivo CSV",
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'form-control'
        })
    )
    
    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        if not archivo.name.endswith('.csv'):
            raise forms.ValidationError("Solo se permiten archivos CSV")
        return archivo

#-----------------------------------------------------------------------------------------------------------------
# ------------------- PARA EL SELECT DEL REGISTRO ARCHIVOS --------------------
# ----------------------------------------------------------------------------------------------------------------

class GrupoContableSelect2Widget(ModelSelect2Widget):
    search_fields = [
        'nombre__icontains',
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'data-placeholder': 'Seleccione grupo contable...',
            'data-minimum-input-length': 0, 
            'data-allow-clear': 'true',
        })

class AuxiliarDependienteSelect2Widget(ModelSelect2Widget):
    search_fields = [
        'nombre__icontains',
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'data-placeholder': 'Primero seleccione un grupo contable...',
            'data-minimum-input-length': 0,
            'disabled': True,
        })

    def get_queryset(self):
        return AuxiliarContable.objects.none()

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        if queryset is None:
            queryset = self.get_queryset()
        
        # Obtener el ID del grupo contable de los parámetros GET
        grupo_contable_id = request.GET.get('grupo_contable_id')
        
        print(f"🔍 DEBUG: grupo_contable_id = {grupo_contable_id}")  # Para debug
        
        if grupo_contable_id:
            queryset = AuxiliarContable.objects.filter(grupocontable_id=grupo_contable_id)
            if term:
                queryset = queryset.filter(nombre__icontains=term)
        else:
            queryset = AuxiliarContable.objects.none()
        
        return queryset

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        # Agregar data attribute para que JavaScript sepa de la dependencia
        attrs['data-depends-on'] = 'id_grupoContable'
        return attrs

class ActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        fields = '__all__'
        widgets = {
            'grupoContable': GrupoContableSelect2Widget(
                attrs={
                    'class': 'form-control border border-info',
                    'id': 'id_grupoContable'
                }
            ),
            'auxiliar': AuxiliarDependienteSelect2Widget(
                attrs={
                    'class': 'form-control border border-info',
                    'id': 'id_auxiliar'
                }
            ),
            'estadoActivo': forms.Select(attrs={
                'class': 'form-control border border-info',
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control border border-info',
                'placeholder': 'Ej: ACT-001'
            }),
            'descActivo': forms.Textarea(attrs={
                'class': 'form-control border border-info',
                'rows': 5,
                'placeholder': 'Descripción del activo...'
            }),
        }

#-----------------------------------------------------------------------------------------------------------------
# ------------------- ACTUALIZAR ACTIVOS --------------------
# ----------------------------------------------------------------------------------------------------------------

class A_Activo(forms.ModelForm):
    class Meta:
        model = Activo
        fields = ['estadoActivo', 'mantenimiento']
        widgets = {
             'estadoActivo': forms.Select(attrs={
                'class': 'form-control border border-info',
            }),
        }

class A_Mantenimiento_I(forms.ModelForm):
    class Meta:
        model = MantenimientoActivo
        fields = ['descripcionInicio']
        widgets = {
             'descripcionInicio': forms.Select(attrs={
                'class': 'form-control border border-info',
            }),
        }
class A_Mantenimiento_F(forms.ModelForm):
    class Meta:
        model = MantenimientoActivo
        fields = ['asignadorFin']
        widgets = {
             'asignadorFin': forms.Select(attrs={
                'class': 'form-control border border-info',
            }),
        }