import csv
import chardet

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.db import transaction

from activos.models import GrupoContable, AuxiliarContable, Activo, Line_Activo
from users.models import User, Personal, Persona
from designacion.models import Activo_responsable

from activos.forms import CargaCSVForm
from revision.views import get_menu_context

class ListaGruposContables(LoginRequiredMixin, ListView):
    model = GrupoContable
    template_name = "lista/GrupoContable.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        context["titulo"] = "LISTA DE GRUPO CONTABLES"
        context["object_list"] = self.model.objects.all()
        usuario = self.request.user
        return context

class ListaAuxiliatesContables(LoginRequiredMixin, ListView):
    model = AuxiliarContable
    template_name = "lista/AuxiliaresContables.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        context["titulo"] = "LISTA DE AUXILIARES CONTABLES"
        context["object_list"] = self.model.objects.all()
        usuario = self.request.user
        return context

class verAuxiliares(LoginRequiredMixin, TemplateView):
    model = AuxiliarContable
    template_name = "Visualizar/Grupo_auxiliar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
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
        context.update(get_menu_context(self.request))
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
                    
                    grupo, created = GrupoContable.objects.get_or_create(
                        nombre=nombre
                    )
                    
                    registros_procesados += 1
                    
                except Exception as e:
                    errores.append(f"Fila {numero_fila}: {str(e)}")
            
            # Mostrar resultados
            if errores:
                messages.warning(request, 
                    f"{registros_procesados} grupos procesados. "
                    f"{len(errores)} errores. "
                    f"Primer error: {errores[0]}")
            else:
                messages.success(request, f"Todos los {registros_procesados} grupos procesados exitosamente!")
            
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
                    f"{registros_procesados} auxiliares procesados. "
                    f"{len(errores)} errores. "
                    f"Primer error: {errores[0]}")
            else:
                messages.success(request, f"Todos los {registros_procesados} auxiliares procesados exitosamente!")
            
        except Exception as e:
            messages.error(request, f"Error procesando archivo: {str(e)}")
        
        return render(request, self.template_name, self.get_context_data())

#-----------------------------------------------------------------------------------------------------------------
# ------------------- CARGA MASIVA DE ACTIVOS FIJOS --------------------
# ----------------------------------------------------------------------------------------------------------------

class CargaDirectaActivosView(TemplateView):
    template_name = 'Carga/Activo.html'
    
    def post(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo')
        
        if not archivo:
            messages.error(request, "Debe seleccionar un archivo CSV")
            return self.get(request, *args, **kwargs)
        
        resultados = self.procesar_archivo_directo(archivo, request)
        
        if resultados['errores'] > 0:
            messages.warning(request, 
                f"{resultados['procesados']} activos procesados, "
                f"{resultados['errores']} errores. "
                f"Revise el formato del archivo.")
        else:
            messages.success(request, f"Todos los {resultados['procesados']} activos procesados exitosamente!")
        
        return self.get(request, *args, **kwargs)
    
    def detectar_separador(self, primera_linea):
        if '\t' in primera_linea:
            return '\t'  
        else:
            return ','  
    
    def normalizar_encabezados(self, encabezados):
        """Normaliza los nombres de los encabezados a minúsculas"""
        return [header.strip().lower() for header in encabezados]
    
    def procesar_archivo_directo(self, archivo, request):
        resultados = {
            'procesados': 0,
            'errores': 0,
            'detalles_errores': []
        }
        
        try:
            raw_data = archivo.read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            contenido = raw_data.decode(encoding)
            lineas = contenido.splitlines()
            
            if not lineas:
                raise ValueError("El archivo está vacío")
            
            separador = self.detectar_separador(lineas[0])
            
            separador_texto = "TABULADOR" if separador == '\t' else "COMA"
            reader = csv.DictReader(lineas, delimiter=separador, quotechar='"')
            reader.fieldnames = self.normalizar_encabezados(reader.fieldnames)
            for numero_fila, fila in enumerate(reader, start=2):
                try:
                    self.procesar_fila_activo(fila, request, numero_fila)
                    resultados['procesados'] += 1
                    
                except Exception as e:
                    resultados['errores'] += 1
                    resultados['detalles_errores'].append({
                        'fila': numero_fila,
                        'error': str(e),
                        'datos': fila
                    })
                    #print("Error fila " + str(numero_fila) + ": " + str(e))
                    #print("Datos de la fila: " + str(fila))
            
        except Exception as e:
            resultados['errores'] += 1
            resultados['detalles_errores'].append({
                'fila': 0,
                'error': "Error general: " + str(e),
                'datos': {}
            })
            #print("Error general: " + str(e))
        
        return resultados
    
    def procesar_fila_activo(self, fila, request, numero_fila):
        codigo = fila.get('codigo', fila.get('Codigo', '')).strip()
        descActivo = fila.get('descactivo', fila.get('descActivo', '')).strip()
        grupo_nombre = fila.get('grupocontable', fila.get('grupoContable', '')).strip()
        auxiliar_nombre = fila.get('auxiliar', '').strip()
        estadoActivo = fila.get('estadoactivo', fila.get('estadoActivo', '')).strip()
        responsable_ci = ''
        piso_ubicacion = 'Almacen'
        oficina_ubicacion = 'Almacen'
        # Validaciones básicas
        if not codigo:
            raise ValueError("El código es obligatorio")
        if not descActivo:
            raise ValueError("La descripción es obligatoria")
        if not grupo_nombre:
            raise ValueError("El grupo contable es obligatorio")
        if not auxiliar_nombre:
            raise ValueError("El auxiliar contable es obligatorio")
        
        # Buscar Grupo Contable
        try:
            grupo = GrupoContable.objects.get(nombre=grupo_nombre)
        except GrupoContable.DoesNotExist:
            raise ValueError("Grupo contable '" + grupo_nombre + "' no existe")
        
        # Buscar Auxiliar Contable
        try:
            auxiliar = AuxiliarContable.objects.get(
                nombre=auxiliar_nombre, 
                grupocontable=grupo
            )
        except AuxiliarContable.DoesNotExist:
            raise ValueError("Auxiliar '" + auxiliar_nombre + "' no existe en el grupo '" + grupo_nombre + "'")
        
        # Determinar estadoDesignacion (True si hay responsable)
        estado_designacion = bool(responsable_ci)
        
        # Buscar o asignar responsable
        responsable = self.buscar_o_asignar_responsable(responsable_ci, request, numero_fila)
        
        # Crear o actualizar Activo
        if Activo.objects.filter(codigo=codigo).exists():
            messages.warning(request, f'El activo con codigo {codigo}, ya esta registrado')
        else:
            activo = Activo.objects.create(
                codigo=codigo,
                descActivo=descActivo,
                grupoContable=grupo,
                auxiliar=auxiliar,
                estadoActivo=estadoActivo or 'Regular',
                estadoDesignacion=estado_designacion,
                mantenimiento=False,
            )        
            # Crear o actualizar Activo_responsable
            Activo_responsable.objects.update_or_create(
                activo=activo,
                defaults={
                    'responsable': responsable,
                    'piso_ubicacion': piso_ubicacion or None,
                    'oficina_ubicacion': oficina_ubicacion or None,
                }
            )
            Line_Activo.objects.create(
                activo = activo,
                creador = request.user,
                estadoActivo = estadoActivo,
                estadoDesignacion = False,
                mantenimiento = False,
                observacion = f'Creado Mediante Carga Masiva',
            )

    def buscar_o_asignar_responsable(self, responsable_ci, request, numero_fila):
        if not responsable_ci:
            # Si no hay responsable en CSV, asignar al usuario actual
            try:                
                user_activo = request.user
                user = User.objects.get(username=user_activo)
                return Personal.objects.get(user=user)
            except Personal.DoesNotExist:
                raise ValueError("No se pudo asignar responsable automáticamente")
        
        # Buscar por diferentes campos
        try:
            carnet = Persona.objects.get(carnet=responsable_ci)            
            return Personal.objects.get(persona=carnet)
        except Personal.DoesNotExist:
            user_activo = request.user
            user = User.objects.get(username=user_activo)
            return Personal.objects.get(user=user)

#-----------------------------------------------------------------------------------------------------------------
# ------------------- CARGA MASIVA DE PERSONAL --------------------
# ----------------------------------------------------------------------------------------------------------------

class CargaMasivaPersonalView(TemplateView):
    template_name = 'Carga/personal.html'
    
    def post(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo')
        
        if not archivo:
            messages.error(request, "Debe seleccionar un archivo CSV")
            return self.get(request, *args, **kwargs)
        
        resultados = self.procesar_archivo_personal(archivo, request)
        
        if resultados['errores'] > 0:
            messages.warning(request, 
                f"{resultados['procesados']} personas procesadas, "
                f"{resultados['errores']} errores.")
        else:
            messages.success(request, f"✅ Todas las {resultados['procesados']} personas procesadas exitosamente!")
        
        return self.get(request, *args, **kwargs)
    
    def procesar_archivo_personal(self, archivo, request):
        resultados = {
            'procesados': 0,
            'errores': 0,
            'detalles_errores': []
        }
        
        try:
            raw_data = archivo.read()
            encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'
            
            contenido = raw_data.decode(encoding)
            
            separador = self.detectar_separador(contenido.splitlines()[0] if contenido.splitlines() else '')
            
            reader = csv.DictReader(contenido.splitlines(), delimiter=separador, quotechar='"')
            
            reader.fieldnames = [header.strip().lower() for header in reader.fieldnames] if reader.fieldnames else []
            print("Encabezados detectados: " + str(reader.fieldnames))
            
            for numero_fila, fila in enumerate(reader, start=2):
                try:
                    with transaction.atomic():
                        self.procesar_fila_personal(fila, request, numero_fila)
                        resultados['procesados'] += 1
                    
                except Exception as e:
                    resultados['errores'] += 1
                    resultados['detalles_errores'].append({
                        'fila': numero_fila,
                        'error': str(e),
                        'datos': fila
                    })
                    print("Error fila " + str(numero_fila) + ": " + str(e))
            
        except Exception as e:
            resultados['errores'] += 1
            resultados['detalles_errores'].append({
                'fila': 0,
                'error': "Error general: " + str(e),
                'datos': {}
            })
        
        return resultados
    
    def detectar_separador(self, primera_linea):
        if '\t' in primera_linea:
            return '\t'
        else:
            return ','
    
    def procesar_fila_personal(self, fila, request, numero_fila):
        nombre = fila.get('nombre', '').strip()
        apellido = fila.get('apellido', '').strip()
        cargo = fila.get('cargo', '').strip()
        contacto = fila.get('contacto', '').strip()
        carnet = fila.get('carnet', '').strip()
        rubrica = fila.get('mosca', '').strip()
        username = fila.get('username', '').strip()
        
        print("Procesando fila " + str(numero_fila) + ":")
        print("  Nombre: " + nombre)
        print("  Apellido: " + apellido)
        print("  Cargo: " + cargo)
        print("  Username: " + username)
        print("  Carnet: " + carnet)
        
        if not nombre:
            raise ValueError("El nombre es obligatorio")
        if not apellido:
            raise ValueError("El apellido es obligatorio")
        if not username:
            raise ValueError("El username es obligatorio")
        if not carnet:
            raise ValueError("El carnet es obligatorio")
        if not cargo:
            raise ValueError("El cargo es obligatorio")
        if not rubrica:
            raise ValueError("La Mosca es obligatorio")
        
        try:
            contacto_int = int(contacto) if contacto else 0
        except ValueError:
            raise ValueError("El contacto debe ser un número válido")
        
        try:
            carnet_int = int(carnet)
        except ValueError:
            messages.error(request, "El carnet debe ser un número válido")
            raise ValueError("El carnet debe ser un número válido")
        
        if Persona.objects.filter(carnet=carnet_int).exists():
            messages.error(request, f"Ya existe una persona con carnet: {carnet}")
            raise ValueError("Ya existe una persona con carnet: " + carnet)
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Ya existe una persona con username: {username}")
            raise ValueError("Ya existe un usuario con username: " + username)
        
        persona = Persona.objects.create(
            nombre=nombre,
            apellido=apellido,
            cargo=cargo or 'Sin cargo',
            contacto=contacto_int,
            carnet=carnet_int,
            rubrica=rubrica or 'N/A'
        )        
        user = User.objects.create_user(
            username=username,
            password=carnet,
            is_active=True,
            is_personal=True,
        )        
        personal = Personal.objects.create(
            persona=persona,
            user=user
        )