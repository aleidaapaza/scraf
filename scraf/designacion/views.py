from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from datetime import date


from designacion.models import Asignacion, Activo_responsable, Line_Asignacion, Line_Activo_Responsable, Devoluciones
from users.models import User, Personal, Persona
from activos.models import Activo, Line_Activo
from activos.choices import pisos_ubicacion,  oficinas_ubicacion

from revision.views import get_menu_context
# Create your views here.

class ListaAsignacionesPersona(LoginRequiredMixin, ListView):
    model = Asignacion
    template_name = "lista/asignaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        user = self.request.user
        users = User.objects.get(username=user)
        persona = Personal.objects.get(user=users)
        context["titulo"] = "LISTA DE ACTIVOS EN LA INSTITUCION"

        context["object_list"] = self.model.objects.filter(carnet=persona.persona.carnet).order_by('-id')
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        if usuario_d.g_Activos:           
            context["entity_registro"] = reverse_lazy("designacion:registrar_asig", args=[])
            context["entity_registro_nom"] = "REGISTRAR NUEVA ASIGNACION"
            context["entity_registro2"] = reverse_lazy("designacion:devolver_asig")
            context["entity_registro_nom2"] = "REGISTRAR NUEVA DEVOLUCION"
        return context
    
class ListaAsignaciones(LoginRequiredMixin, ListView):
    model = Asignacion
    template_name = "lista/asignaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        context["titulo"] = "LISTA DE ASIGNACIONES Y DEVOLUCIONES EN LA INSTITUCION"
        context["object_list"] = self.model.objects.all().order_by('-id')
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        if usuario_d.g_Activos:           
            context["entity_registro"] = reverse_lazy("designacion:registrar_asig", args=[])
            context["entity_registro_nom"] = "REGISTRAR NUEVA ASIGNACION"
            context["entity_registro2"] = reverse_lazy("designacion:devolver_asig")
            context["entity_registro_nom2"] = "REGISTRAR NUEVA DEVOLUCION"
        return context

@login_required
def crear_asignacion(request):
    if request.method == 'POST':
        try:
            personal_slug = request.POST.get('personal')
            activos_seleccionados = request.POST.getlist('activos')
            if not personal_slug or not activos_seleccionados:
                messages.error(request, 'Debe seleccionar un personal y al menos un activo')
                return redirect('designacion:registrar_asig')  
            personal = Personal.objects.get(slug=personal_slug)            
            asignacion = Asignacion.objects.create(
                estado=True,
                carnet=personal.persona.carnet if personal.persona else 0, 
                cargo=personal.persona.cargo if personal.persona else "Sin cargo",
                codigoActivo=activos_seleccionados
            )
            Line_Asignacion.objects.create(
                slug = asignacion,
                estado = asignacion.estado,
                observacion = f"REGISTRO DE ASIGNACION, CARNET:{asignacion.carnet} CARGO:{asignacion.cargo} CODIGOS DE ACTIVOS:{asignacion.codigoActivo}"
            )
            for codigo_activo in activos_seleccionados:
                activo = Activo.objects.get(codigo=codigo_activo)                
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
                    activo_responsable.asignacion = asignacion
                    activo_responsable.responsable = personal
                    activo_responsable.save()

                Line_Activo_Responsable.objects.create(
                    slug=activo,
                    creador=request.user,
                    responsable=personal,
                    estado="Asignado",
                    observacion="Se realizo la asignacion con codigo:{}".format(asignacion.slug)
                )
                activo.estadoDesignacion = True
                activo.save()
                Line_Activo.objects.create(
                    activo=activo,
                    creador=request.user,
                    estadoActivo=activo.estadoActivo,
                    estadoDesignacion=activo.estadoDesignacion,
                    mantenimiento=activo.mantenimiento,
                    observacion="Se realizo la asignacion del activo al Personal con carnet:{}".format(asignacion.carnet)
                )
            return redirect('designacion:confirmacionUbicacion', tipo='asignacion', slug=asignacion.slug)
        
        except Personal.DoesNotExist:
            return JsonResponse({'error': 'Personal no encontrado'}, status=400)
        except Activo.DoesNotExist:
            return JsonResponse({'error': 'Uno o más activos no encontrados'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        personal_list = Personal.objects.select_related('persona', 'user').all()        
        activos_no_asignados = Activo.objects.filter(estadoDesignacion=False).exclude(mantenimiento=True)        
        context = {
            'subtitulo_1': 'Seleccionar Personal',
            'subtitulo_2': 'Activos Disponibles',
            'personal_list': personal_list,
            'activos_list': activos_no_asignados,
            'accion': 'Guardar Asignación',
            'accion2': 'Cancelar',
            'accion2_url': reverse('designacion:lista_asignaciones'), 
            'form_action_url': reverse('designacion:registrar_asig')
        }
        context.update(get_menu_context(request))

        return render(request, 'RegistroActualizacion/asignacion.html', context)

@login_required
def crear_devolucion(request):
    if request.method == 'POST':
        try:
            asignacion_slug = request.POST.get('asignacion')
            activos_devueltos = request.POST.getlist('activos_devueltos')
            tipo_devolucion = request.POST.get('tipo_devolucion')
            observaciones = request.POST.get('observaciones', '')

            mantenimiento = []
            for activos in activos_devueltos:
                activo = Activo.objects.get(codigo=activos)
                if activo.mantenimiento:
                    mantenimiento.append(activo)
            if mantenimiento:
                activos_mantenimiento = []
                for activo in mantenimiento:
                    activos_mantenimiento.append(activo.codigo)
                messages.error(request, f"No se puede hacer la devolucion los activo: {activos_mantenimiento} se encuentra en mantenimiento")
                asignaciones_activas = Asignacion.objects.filter(estado=True)        
                context = {
                        'subtitulo_1': 'Seleccionar Asignación',
                        'subtitulo_2': 'Activos a Devolver',
                        'asignaciones_list': asignaciones_activas,
                        'accion': 'Guardar Devolucion',
                        'accion2': 'Cancelar',
                        'accion2_url': reverse('designacion:lista_asignaciones'),
                        'form_action_url': reverse('designacion:devolver_asig')
                    }        
                context.update(get_menu_context(request))
                return render(request, 'RegistroActualizacion/devolucion.html', context)

            if not asignacion_slug or not activos_devueltos:
                messages.error(request, 'Debe seleccionar una asignación y al menos un activo')
                return redirect('designacion:devolver_asig')
            
            asignacion = Asignacion.objects.get(slug=asignacion_slug)

            if len(activos_devueltos) == len(asignacion.codigoActivo):
                tipo_devolucion = "Total"
            else:
                tipo_devolucion = "Parcial"

            devolucion = Devoluciones.objects.create(
                asignacion=asignacion,
                tipoDevolucion=tipo_devolucion,
                codigoActivo=activos_devueltos,
                observaciones=observaciones 
            )

            for codigo_activo in activos_devueltos:
                try:
                    activo = Activo.objects.get(codigo=codigo_activo)                    
                    activo.estadoDesignacion = False
                    activo.save()
                    crear_linea = Line_Activo.objects.create(
                        activo=activo,
                        creador=request.user,
                        estadoActivo=activo.estadoActivo,
                        estadoDesignacion=activo.estadoDesignacion,
                        mantenimiento=activo.mantenimiento,
                        observacion=f"Se realizó la DEVOLUCION de este activo de la asignación {asignacion.slug}"
                    )                    
                except Activo.DoesNotExist:
                    messages.error(request, f'Activo con código {codigo_activo} no existe')
                    continue
                except Exception as e_activo:
                    messages.error(request, f'Error creando Line_Activo para {codigo_activo}: {str(e_activo)}')
                    import traceback
                    messages.error(request, f'Traceback: {traceback.format_exc()}')
                    continue
            activos_asignados_originalmente = asignacion.codigoActivo
            activos_devueltos_total = []            
            devoluciones_asignacion = Devoluciones.objects.filter(asignacion=asignacion)
            for dev in devoluciones_asignacion:
                activos_devueltos_total.extend(dev.codigoActivo)            
            if set(activos_asignados_originalmente) == set(activos_devueltos_total):
                asignacion.estado = False
                asignacion.save()
                Line_Activo.objects.create(
                    activo=activo,
                    creador=request.user,
                    estadoActivo=activo.estadoActivo,
                    estadoDesignacion=activo.estadoDesignacion,
                    mantenimiento=activo.mantenimiento,
                    observacion="Se realizo la DEVOLUCION del activo al Personal con carnet:{}".format(asignacion.carnet)
                )
                messages.success(request, 'Devolución completada - TODOS los activos devueltos - Asignación cerrada')                
                Line_Asignacion.objects.create(
                    slug = asignacion,
                    estado = asignacion.estado,
                    observacion = f"REGISTRO DE DEVOLUCION TIPO {devolucion.tipoDevolucion}, DE LOS CODIGOS DE ACTIVOS:{activos_devueltos}. SE CONCLUYO CON LA DEVOLUCION DE TODOS LOS ACTIVOS"
                )
            else:
                messages.success(request, f'Devolución parcial registrada - {len(activos_devueltos)} activo(s) devuelto(s)')                
                Line_Asignacion.objects.create(
                    slug = asignacion,
                    estado = asignacion.estado,
                    observacion = f"REGISTRO DE DEVOLUCION {devolucion.tipoDevolucion}, CODIGOS DE ACTIVOS:{activos_devueltos}"
                )
            return redirect('designacion:confirmacionUbicacion', tipo='devolucion', slug=devolucion.id)            
        except Asignacion.DoesNotExist:
            messages.error(request, 'Asignación no encontrada')
            return redirect('designacion:devolver_asig')
        except Activo.DoesNotExist:
            messages.error(request, 'Uno o más activos no encontrados')
            return redirect('designacion:devolver_asig')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('designacion:devolver_asig')
    else:
        asignaciones_activas = Asignacion.objects.filter(estado=True)        
        context = {
            'subtitulo_1': 'Seleccionar Asignación',
            'subtitulo_2': 'Activos a Devolver',
            'asignaciones_list': asignaciones_activas,
            'accion': 'Guardar Devolucion',
            'accion2': 'Cancelar',
            'accion2_url': reverse('designacion:lista_asignaciones'),
            'form_action_url': reverse('designacion:devolver_asig')
        }        
        context.update(get_menu_context(request))
        return render(request, 'RegistroActualizacion/devolucion.html', context)
    
@login_required
def get_activos_asignacion(request):
    if request.method == 'GET' and request.GET.get('asignacion_slug'):
        asignacion_slug = request.GET.get('asignacion_slug')        
        try:
            asignacion = Asignacion.objects.get(slug=asignacion_slug, estado=True)
            activos_codigos = asignacion.codigoActivo
            activos_detalle = []
            for codigo in activos_codigos:
                try:
                    activo = Activo.objects.get(codigo=codigo)
                    devuelto = Devoluciones.objects.filter(
                        asignacion=asignacion, 
                        codigoActivo__contains=[codigo]
                    ).exists()                    
                    activos_detalle.append({
                        'codigo': activo.codigo,
                        'descripcion': activo.descActivo,
                        'grupo_contable': activo.grupoContable.nombre if activo.grupoContable else '',
                        'ya_devuelto': devuelto,
                        'estado_designacion': activo.estadoDesignacion
                    })
                except Activo.DoesNotExist:
                    continue            
            return JsonResponse({
                'success': True,
                'activos': activos_detalle,
                'total_activos': len(activos_codigos)
            })            
        except Asignacion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Asignación no encontrada'})    
    return JsonResponse({'success': False, 'error': 'Solicitud inválida'})

@login_required
def confirmar_ubicacion(request, tipo, slug):    
    if tipo == 'asignacion':
        asignacion = get_object_or_404(Asignacion, slug=slug)
        activos_codigos = asignacion.codigoActivo
        titulo = f"Confirmar Ubicación - Asignación: {asignacion.slug}"
        
    elif tipo == 'devolucion':
        devolucion = get_object_or_404(Devoluciones, id=slug)
        asignacion = devolucion.asignacion
        activos_codigos = devolucion.codigoActivo
        titulo = f"Confirmar Ubicación - Devolución: {devolucion.asignacion.slug}"    
    else:
        messages.error(request, 'Tipo de operación no válido')
        return redirect('designacion:lista_asignaciones')
    activos_responsable = Activo_responsable.objects.filter(
        activo__codigo__in=activos_codigos,
        asignacion=asignacion
    ).select_related('activo')    
    if request.method == 'POST':
        try:
            for activo_resp in activos_responsable:
                id_activo = activo_resp.pk

                piso_anterior = activo_resp.piso_ubicacion
                oficina_anterior = activo_resp.oficina_ubicacion

                piso_key = f"piso_{activo_resp.activo.codigo}"
                oficina_key = f"oficina_{activo_resp.activo.codigo}"
                
                piso_ubicacion = request.POST.get(piso_key)
                oficina_ubicacion = request.POST.get(oficina_key)

                activo_resp.piso_ubicacion = piso_ubicacion
                activo_resp.oficina_ubicacion = oficina_ubicacion
                activo_resp.save()
                activo_act = Activo_responsable.objects.get(id=id_activo)

                observacions = ' '
                if piso_anterior == activo_act.piso_ubicacion:
                    observacions = f'Se mantiene la ubicacion del piso'
                else:
                    observacions = f'Ubicacion cambiada, piso anterior {piso_anterior}'
                if oficina_anterior == activo_act.oficina_ubicacion:
                    observacions = f'{observacions} y de la oficina'
                else:
                    observacions = f'{observacions} y oficina anterior {oficina_anterior}'
                
                try:
                    line_responsable = Line_Activo_Responsable.objects.create(
                        slug=activo_act.activo,
                        creador=request.user,
                        responsable=activo_act.responsable,
                        piso_ubicacion=activo_act.piso_ubicacion,
                        oficina_ubicacion=activo_act.oficina_ubicacion,
                        estado=tipo,
                        observacion=observacions
                    )                   
                except Exception as e_line:
                    messages.error(request, f'ERROR creando Line_Activo_Responsable: {str(e_line)}')
                    messages.error(request, f'Tipo de error: {type(e_line).__name__}')
                    continue
            if tipo == 'devolucion':
                for activo_resp in activos_responsable:
                    id_activo = activo_resp.pk                    
                    try:
                        asignacion_anterior = activo_resp.asignacion
                        responsable_anterior = activo_resp.responsable

                        activo_resp.asignacion = None
                        activo_resp.responsable = None
                        activo_resp.save()

                        activo_act = Activo_responsable.objects.get(id=id_activo)
                        
                        Line_Activo_Responsable.objects.create(
                            slug=activo_act.activo,
                            creador=request.user,
                            responsable=None,  # Ahora es None
                            piso_ubicacion=activo_act.piso_ubicacion,
                            oficina_ubicacion=activo_act.oficina_ubicacion,
                            estado=tipo,
                            observacion=f'El responsable anterior:{responsable_anterior} / Asignacion anterior:{asignacion_anterior}'
                        )
                    except Exception as e:
                        messages.error(request, f'Error limpiando responsable: {str(e)}')
                        continue
            messages.success(request, f'Ubicaciones confirmadas exitosamente')
            if tipo == 'asignacion':
                return redirect('designacion:lista_asignaciones')
            else:
                return redirect('designacion:lista_asignaciones')    
        except Exception as e:
            messages.error(request, f'Error al guardar ubicaciones: {str(e)}')    
    activos_data = []
    for activo_resp in activos_responsable:
        activos_data.append({
            'codigo': activo_resp.activo.codigo,
            'descripcion': activo_resp.activo.descActivo,
            'grupo_contable': activo_resp.activo.grupoContable.nombre if activo_resp.activo.grupoContable else '',
            'piso_actual': activo_resp.piso_ubicacion,
            'oficina_actual': activo_resp.oficina_ubicacion,
            'responsable': activo_resp.responsable
        })    
    context = {
        'titulo': titulo,
        'tipo': tipo,
        'asignacion': asignacion,
        'activos_data': activos_data,
        'pisos_ubicacion': pisos_ubicacion,
        'oficinas_ubicacion': oficinas_ubicacion,
    }
    context.update(get_menu_context(request))
    
    return render(request, 'RegistroActualizacion/ubicacion_confirmar.html', context)

class verAsignaciones(LoginRequiredMixin,TemplateView):
    template_name="lista/verAsignaciones.html"
    model = Asignacion
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        slug = self.kwargs.get("slug")
        asignacion = self.model.objects.get(slug=slug)
        persona = Persona.objects.get(carnet=asignacion.carnet)
        activos = []
        for activosSelect in asignacion.codigoActivo:
            activoSeleccionado = Activo.objects.get(codigo=activosSelect)
            activos.append(activoSeleccionado)
        cantidad = len(activos)
        context["titulo"] = f'DATOS DE LA ASIGNACION {asignacion.slug}'
        context["icono_1"] = "fa-solid fa-user"
        context["subtitulo_1"] = "Datos del Personal"
        context["icono_2"] = "fa-solid fa-plus"
        context["subtitulo_2"] = "Datos de la Asignacion"
        context["asignacion"] = asignacion
        context["persona"] = persona
        context["activos"]=activos
        context["cantidad"]=cantidad
        return context

class verDevolucion(LoginRequiredMixin,TemplateView):
    template_name="lista/verDevolucion.html"
    model = Devoluciones
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        slug = self.kwargs.get("slug")
        asignacion = Asignacion.objects.get(slug=slug)
        devolucion = self.model.objects.filter(asignacion=slug)
        persona = Persona.objects.get(carnet=asignacion.carnet)
        activos = []
        context["titulo"] = f'DATOS DE LA DEVOLUCION {asignacion.slug}'
        context["icono_1"] = "fa-solid fa-user"
        context["subtitulo_1"] = "Datos del Personal"
        context["icono_2"] = "fa-solid fa-minus"
        context["subtitulo_2"] = "Datos de la Devolucion"
        context["persona"] = persona
        context["asignacion"] = asignacion
        context["devoluciones"] = devolucion

        return context

class ListaAsignacionesPersonal(LoginRequiredMixin, ListView):
    model = Asignacion
    template_name = "lista/asignaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        carnet = self.kwargs.get("carnet")
        persona = Persona.objects.get(carnet=carnet)
        personal = Personal.objects.get(persona=persona)
        context["titulo"] = "LISTA DE ACTIVOS EN LA INSTITUCION"

        context["object_list"] = self.model.objects.filter(carnet=personal.persona.carnet).order_by('-id')
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        if usuario_d.g_Activos:           
            context["entity_registro"] = reverse_lazy("designacion:registrar_asig", args=[])
            context["entity_registro_nom"] = "REGISTRAR NUEVA ASIGNACION"
            context["entity_registro2"] = reverse_lazy("designacion:devolver_asig")
            context["entity_registro_nom2"] = "REGISTRAR NUEVA DEVOLUCION"
        return context

class Line_Asignaciones(LoginRequiredMixin,ListView):
    model = Line_Asignacion
    template_name = "lista/line_asignaciones.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        slug = self.kwargs.get("slug")
        context["titulo"] = "LINE DE ASIGNACIONES/DEVOLUCIONES"
        asignacion = Asignacion.objects.get(slug=slug)
        context["object_list"] = self.model.objects.filter(slug=asignacion).order_by('-id')
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        return context
    
