import csv
import chardet

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render

from activos.models import GrupoContable, AuxiliarContable
from users.models import User
from activos.forms import CargaCSVForm

class ListaGruposContables(LoginRequiredMixin, ListView):
    model = GrupoContable
    template_name = "lista/GrupoContable.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "LISTA DE GRUPO CONTABLES"
        context["object_list"] = self.model.objects.all()
        usuario = self.request.user
        return context

class ListaAuxiliatesContables(LoginRequiredMixin, ListView):
    model = AuxiliarContable
    template_name = "lista/AuxiliaresContables.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "LISTA DE AUXILIARES CONTABLES"
        context["object_list"] = self.model.objects.all()
        usuario = self.request.user
        return context

class verAuxiliares(LoginRequiredMixin, TemplateView):
    model = AuxiliarContable
    template_name = "Visualizar/Grupo_auxiliar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get("pk", None)
        context["titulo"] = "GRUPO Y SUS AUXILIARES CONTABLES"
        context["object_list"] = self.model.objects.filter(grupocontable__id = id)
        grupo = GrupoContable.objects.get(id=id)
        context["grupo"] = grupo
        return context
    
class CargaContableView(TemplateView):
    template_name = 'Carga/GrupoContable.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_grupo'] = CargaCSVForm()
        context['form_auxiliar'] = CargaCSVForm()
        return context
    
    def post(self, request, *args, **kwargs):
        tipo_carga = request.POST.get('tipo_carga')
        archivo = request.FILES.get('archivo')
        
        if not archivo:
            messages.error(request, "Debe seleccionar un archivo")
            return self.get(request, *args, **kwargs)
        
        if tipo_carga == 'grupo':
            return self.procesar_grupos_contables(archivo, request)
        elif tipo_carga == 'auxiliar':
            return self.procesar_auxiliares_contables(archivo, request)
        else:
            messages.error(request, "Tipo de carga no válido")
            return self.get(request, *args, **kwargs)
    
    def procesar_grupos_contables(self, archivo, request):
        try:
            raw_data = archivo.read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            contenido = raw_data.decode(encoding)
            reader = csv.DictReader(contenido.splitlines())
            
            registros_procesados = 0
            errores = []
            
            for numero_fila, fila in enumerate(reader, start=2):
                try:
                    nombre = fila.get('nombre', '').strip()
                    
                    if not nombre:
                        raise ValueError("El nombre es obligatorio")
                    
                    # Crear o actualizar Grupo Contable
                    grupo, created = GrupoContable.objects.get_or_create(
                        nombre=nombre
                    )
                    
                    registros_procesados += 1
                    
                except Exception as e:
                    errores.append(f"Fila {numero_fila}: {str(e)}")
            
            # Mostrar resultados
            if errores:
                messages.warning(request, 
                    f"✅ {registros_procesados} grupos procesados. "
                    f"❌ {len(errores)} errores. "
                    f"Primer error: {errores[0]}")
            else:
                messages.success(request, f"✅ Todos los {registros_procesados} grupos procesados exitosamente!")
            
        except Exception as e:
            messages.error(request, f"❌ Error procesando archivo: {str(e)}")
        
        return render(request, self.template_name, self.get_context_data())
    
    def procesar_auxiliares_contables(self, archivo, request):
        try:
            raw_data = archivo.read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            contenido = raw_data.decode(encoding)
            reader = csv.DictReader(contenido.splitlines())
            
            registros_procesados = 0
            errores = []
            
            for numero_fila, fila in enumerate(reader, start=2):
                try:
                    nombre = fila.get('nombre', '').strip()
                    grupo_nombre = fila.get('grupocontable', '').strip()
                    
                    if not nombre:
                        raise ValueError("El nombre del auxiliar es obligatorio")
                    if not grupo_nombre:
                        raise ValueError("El nombre del grupo contable es obligatorio")
                    
                    try:
                        grupo = GrupoContable.objects.get(nombre=grupo_nombre)
                    except GrupoContable.DoesNotExist:
                        raise ValueError(f"Grupo contable '{grupo_nombre}' no existe")
                    auxiliar, created = AuxiliarContable.objects.get_or_create(
                        nombre=nombre,
                        grupocontable=grupo
                    )
                    registros_procesados += 1
                except Exception as e:
                    errores.append(f"Fila {numero_fila}: {str(e)}")
            if errores:
                messages.warning(request, 
                    f"✅ {registros_procesados} auxiliares procesados. "
                    f"❌ {len(errores)} errores. "
                    f"Primer error: {errores[0]}")
            else:
                messages.success(request, f"✅ Todos los {registros_procesados} auxiliares procesados exitosamente!")
            
        except Exception as e:
            messages.error(request, f"❌ Error procesando archivo: {str(e)}")
        
        return render(request, self.template_name, self.get_context_data())