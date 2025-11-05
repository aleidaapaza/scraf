from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.contrib import messages


from designacion.models import Asignacion, Activo_responsable
from users.models import User, Personal
from activos.models import Activo

# Create your views here.
class ListaAsignaciones(LoginRequiredMixin, ListView):
    model = Asignacion
    template_name = "lista/asignaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "LISTA DE ACTIVOS EN LA INSTITUCION"
        context["object_list"] = self.model.objects.all()
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        if usuario_d.g_Activos:           
            context["entity_registro"] = reverse_lazy("designacion:registrar_asig", args=[])
            context["entity_registro_nom"] = "REGISTRAR NUEVA ASIGNACION"
            context["entity_registro2"] = reverse_lazy("activos:ajax_r_activo_resp")
            context["entity_registro_nom2"] = "REGISTRAR NUEVA DEVOLUCION"
        return context

def crear_asignacion(request):
    if request.method == 'POST':
        try:
            personal_slug = request.POST.get('personal')
            activos_seleccionados = request.POST.getlist('activos')
            if not personal_slug or not activos_seleccionados:
                messages.error(request, '❌ Debe seleccionar un personal y al menos un activo')
                return redirect('designacion:registrar_asig')  # Redirige de vuelta al formulario
            personal = Personal.objects.get(slug=personal_slug)            
            # 1. CREAR REGISTRO EN ASIGNACION
            asignacion = Asignacion.objects.create(
                estado=True,
                carnet=personal.persona.carnet if personal.persona else 0,  # Ajusta según tu modelo Persona
                cargo=personal.persona.cargo if personal.persona else "Sin cargo",  # Ajusta según tu modelo
                codigoActivo=activos_seleccionados
            )            
            # 2. CREAR/ACTUALIZAR REGISTROS EN ACTIVO_RESPONSABLE
            for codigo_activo in activos_seleccionados:
                activo = Activo.objects.get(codigo=codigo_activo)
                
                # Buscar si ya existe un registro para este activo
                activo_responsable, created = Activo_responsable.objects.get_or_create(
                    activo=activo,
                    defaults={
                        'asignacion': asignacion,
                        'responsable': personal,
                        'piso_ubicacion': None,
                        'oficina_ubicacion': None
                    }
                )
                
                if not created:
                    # Actualizar el registro existente
                    activo_responsable.asignacion = asignacion
                    activo_responsable.responsable = personal
                    activo_responsable.save()
                
                # Actualizar el estado del activo
                activo.estadoDesignacion = True
                activo.save()
            
            return redirect('nombre_de_tu_vista_exitosa')  # Redirigir a una vista de éxito
            
        except Personal.DoesNotExist:
            return JsonResponse({'error': 'Personal no encontrado'}, status=400)
        except Activo.DoesNotExist:
            return JsonResponse({'error': 'Uno o más activos no encontrados'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - mostrar el formulario
    else:
        # Obtener todos los usuarios/personal disponibles
        personal_list = Personal.objects.select_related('persona', 'user').all()
        
        # Obtener activos no asignados
        activos_no_asignados = Activo.objects.filter(estadoDesignacion=False)
        
        context = {
            'subtitulo_1': 'Seleccionar Personal',
            'subtitulo_2': 'Activos Disponibles',
            'personal_list': personal_list,
            'activos_list': activos_no_asignados,
            'accion': 'Guardar Asignación',
            'accion2': 'Cancelar',
            'accion2_url': 'url_para_cancelar',  # Define tu URL
            'form_action_url': reverse('designacion:registrar_asig')
        }
        
        return render(request, 'RegistroActualizacion/asignacion.html', context)