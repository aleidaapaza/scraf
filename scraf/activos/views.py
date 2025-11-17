import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView

from activos.forms import R_Activo, R_Activo_responsable, A_Activo, ActivoForm, A_Activo, MantenimientoActivoForm
from activos.models import Activo, AuxiliarContable, Line_Activo, MantenimientoActivo
from designacion.models import Activo_responsable, Line_Activo_Responsable
from revision.views import get_menu_context
from users.models import User, Personal

class ListaActivos(LoginRequiredMixin, ListView):
    model = Activo
    template_name = "lista/activo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        context["titulo"] = "LISTA DE ACTIVOS EN LA INSTITUCION"
        context["object_list"] = self.model.objects.all().order_by("id")
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        context.update(get_menu_context(self.request))
        if usuario_d.g_Activos:
            context["entity_registro"] = reverse_lazy("activos:registro_activos", args=[])
            context["entity_registro_nom"] = "REGISTRAR NUEVO ACTIVO"
        return context

class RegistroActivo(LoginRequiredMixin, CreateView):
    model = Activo
    template_name = "RegistroActualizacion/activo.html"
    form_class = ActivoForm
    success_url = reverse_lazy("activos:lista_activos")
    def get_context_data(self, **kwargs):
        context = super(RegistroActivo, self).get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        slug = self.kwargs.get("slug")
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        context["titulo"] = "REGISTRO DEL ACTIVO"
        context["subtitulo_1"] = "REGISTRO DEL ACTIVO"
        context["accion"] = "REGISTRO"
        context["accion2"] = "VOLVER"
        context["accion2_url"] = reverse_lazy("activos:lista_activos")
        return context
    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        form = self.form_class(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data.get("codigo")
            form.save()
            activo = self.model.objects.get(codigo=codigo)
            print('activo registrado', activo)
            Line_Activo.objects.create(
                activo = activo,
                creador = usuario,
                estadoActivo = activo.estadoActivo,
                estadoDesignacion = activo.estadoDesignacion,
                mantenimiento = activo.mantenimiento,
                observacion = "Registro del Activo"
            )
        return HttpResponseRedirect(reverse("activos:lista_activos"))

def get_auxiliares_por_grupo(request):
    grupo_id = request.GET.get('grupo_id')
    search_term = request.GET.get('q', '')
    if not grupo_id:
        return JsonResponse([], safe=False)
    try:
        auxiliares = AuxiliarContable.objects.filter(grupocontable_id=grupo_id)
        if search_term:
            auxiliares = auxiliares.filter(nombre__icontains=search_term)
        data = []
        for auxiliar in auxiliares:
            data.append({
                'id': auxiliar.id,
                'text': auxiliar.nombre
            })
        
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        return JsonResponse([], safe=False)

class LineActivo(LoginRequiredMixin, TemplateView):
    template_name = "lista/lineActivo.html"
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context.update(get_menu_context(self.request))
            codigo = self.kwargs.get("codigo")
            activo = Activo.objects.get(codigo=codigo)
            activo_line = Line_Activo.objects.filter(activo=activo)
            activo_responsable_line = Line_Activo_Responsable.objects.filter(slug=activo).order_by("-fecha_registro")
            mantenimiento = MantenimientoActivo.objects.filter(activo = activo).order_by("-fechaInicio")
            context["titulo"] = "INFORMACION DEL ACTIVO"
            context["subtitulo_1"] = "LINE MODIFICACION DATOS ACTIVOS"
            context["subtitulo_2"] = "LINE MODIFICACION DESIGNACIONES ACTIVOS"
            context["subtitulo_3"] = "LINE MANTENIMIENTO ACTIVOS"
            context["activo"] = activo
            context["line_actvo"] = activo_line
            context["activo_responsable_line"] = activo_responsable_line
            context["mantenimiento"] = mantenimiento

            return context

class VerActivo(LoginRequiredMixin, TemplateView):
    template_name = "Visualizar/activo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        slug = self.kwargs.get("codigo")
        activo = Activo.objects.get(codigo=slug)
        context["titulo"] = "INFORMACION DEL ACTIVO"
        context["activo"] = activo
        lugar = Activo_responsable.objects.filter(activo=activo)
        if lugar:
            lugar = lugar.first()
            context["responsable"] = lugar
        mantenimiento = MantenimientoActivo.objects.filter(activo=activo, estado = True)
        print('mantenimiento', mantenimiento)
        if mantenimiento:
            mantenimientos = mantenimiento.first()
            context["mantenimientos"] = mantenimientos
        return context    

#-----------------------------------------------------------------------------------------------------------------
# ------------------- actualizar datos activo y habilitar mantenimiento --------------------
# ----------------------------------------------------------------------------------------------------------------

def gestionar_activo(request, activo_codigo):
    activo = get_object_or_404(Activo, codigo=activo_codigo)
    try:
        mantenimiento_activo = MantenimientoActivo.objects.get(
            activo=activo, 
            estado=True 
        )
    except MantenimientoActivo.DoesNotExist:
        mantenimiento_activo = None    
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':            
            if request.POST.get('form_type') == 'form_activo':                
                form_activo = A_Activo(
                    request.POST, 
                    instance=activo
                )
                if form_activo.is_valid():
                    instancia = form_activo.save()
                    activo = Activo.objects.get(codigo=instancia.codigo)
                    Line_Activo.objects.create(
                        activo = activo,
                        creador = request.user,
                        estadoActivo = activo.estadoActivo,
                        estadoDesignacion = activo.estadoDesignacion,
                        mantenimiento = activo.mantenimiento,
                        observacion = "Cambio de Estado"
                    )
                    return JsonResponse({
                        'success': True, 
                        'message': 'Estado del activo actualizado correctamente',
                        'codigo': instancia.codigo,
                    })
                else:
                    return JsonResponse({
                        'success': False, 
                        'errors': form_activo.errors
                    })
            
            elif request.POST.get('form_type') == 'form_mantenimiento':
                if request.POST.get('accion') == 'iniciar':
                    form_mantenimiento = MantenimientoActivoForm(request.POST)
                    if form_mantenimiento.is_valid():
                        instancia = form_mantenimiento.save(commit=False)
                        instancia.activo = activo
                        instancia.estado = True  # Activo
                        instancia.fechaInicio = timezone.now().date()
                        try:
                            personal_usuario = Personal.objects.get(user=request.user)
                            instancia.asignadorInicio = personal_usuario
                        except Personal.DoesNotExist:
                            return JsonResponse({
                                    'success': False, 
                                    'errors': {'general': 'El usuario no tiene un perfil de Personal asociado'}
                                })
                        instancia.save()
                        
                        activo.mantenimiento = True
                        activo.save()
                        Line_Activo.objects.create(
                            activo = activo,
                            creador = request.user,
                            estadoActivo = activo.estadoActivo,
                            estadoDesignacion = activo.estadoDesignacion,
                            mantenimiento = activo.mantenimiento,
                            observacion = "Inicio de Mantenimiento"
                        )
                        return JsonResponse({
                            'success': True, 
                            'message': 'Mantenimiento iniciado correctamente',
                            'estado': 'activo'
                        })
                    else:
                        return JsonResponse({
                            'success': False, 
                            'errors': form_mantenimiento.errors
                        })
                
                elif request.POST.get('accion') == 'finalizar':
                    # Finalizar mantenimiento existente
                    if mantenimiento_activo:
                        form_mantenimiento = MantenimientoActivoForm(
                            request.POST, 
                            instance=mantenimiento_activo
                        )
                        if form_mantenimiento.is_valid():
                            instancia = form_mantenimiento.save(commit=False)
                            instancia.estado = False  # Inactivo
                            instancia.fechaFin = timezone.now().date()
                            try:
                                personal_usuario = Personal.objects.get(user=request.user)
                                instancia.asignadorFin = personal_usuario
                            except Personal.DoesNotExist:
                                # Manejar el caso donde el usuario no tiene perfil Personal
                                return JsonResponse({
                                    'success': False, 
                                    'errors': {'general': 'El usuario no tiene un perfil de Personal asociado'}
                                })
                            instancia.save()
                            activo.mantenimiento = False
                            activo.save()
                            Line_Activo.objects.create(
                                activo = activo,
                                creador = request.user,
                                estadoActivo = activo.estadoActivo,
                                estadoDesignacion = activo.estadoDesignacion,
                                mantenimiento = activo.mantenimiento,
                                observacion = "FIN de Mantenimiento"
                            )
                            return JsonResponse({
                                'success': True, 
                                'message': 'Mantenimiento finalizado correctamente',
                                'estado': 'inactivo'
                            })
                        else:
                            return JsonResponse({
                                'success': False, 
                                'errors': form_mantenimiento.errors
                            })
    
    form_activo = A_Activo(instance=activo)
    form_mantenimiento = MantenimientoActivoForm(instance=mantenimiento_activo)
    
    context = {
        'form_activo': form_activo,
        'form_mantenimiento': form_mantenimiento,
        'activo': activo,
        'mantenimiento_activo': mantenimiento_activo,
        'subtitulo_1': 'Estado del Activo',
        'subtitulo_2': 'Gestión de Mantenimiento',
    }
    context.update(get_menu_context(request))
    return render(request, 'RegistroActualizacion/activo_a.html', context)

#-----------------------------------------------------------------------------------------------------------------
# ------------------- VIEWS ANTIGUROS ACTIVOS --------------------
# ----------------------------------------------------------------------------------------------------------------

class ActualizarActivo(LoginRequiredMixin, UpdateView):
    model = Activo
    second_model = MantenimientoActivo
    template_name = "RegistroActualizacion/activo_a.html"
    form_class = R_Activo_responsable
    def get_context_data(self, **kwargs):
        context = super(RegistroActivoResponsable, self).get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        if "form" not in context:
            context["form"] = self.form_class(self.request.GET)
        if "form2" not in context:
            context["form2"] = self.second_form_class(self.request.GET)
        context["titulo"] = "ACTUALIZACION DE DATOS DEL ACTIVO"
        context["subtitulo_1"] = "ACTUALIZAR DATOS DEL ACTIVO"
        context["subtitulo_2"] = "MANTENIMIENTO"
        context["accion"] = "GUARDAR"
        context["accion2"] = "CANCELAR"
        context["accion2_url"] = reverse_lazy("activos:lista_activos")
        context["activate"] = True
        return context

class RegistroActivoResponsable(LoginRequiredMixin, CreateView):
    model = Activo_responsable
    second_model = Activo
    template_name = "RegistroActualizacion/activo.html"
    form_class = R_Activo_responsable
    second_form_class = R_Activo
    success_url = reverse_lazy("activos:lista_activos")

    def get_context_data(self, **kwargs):
        context = super(RegistroActivoResponsable, self).get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        if "form" not in context:
            context["form"] = self.form_class(self.request.GET)
        if "form2" not in context:
            context["form2"] = self.second_form_class(self.request.GET)
        context["titulo"] = "REGISTRO INFORMACION ACTIVO Y RESPONSABLE DEL ACTIVO"
        context["subtitulo_1"] = "DATOS DEL RESPONSABLE"
        context["subtitulo_2"] = "DATOS DEL ACTIVO"
        context["accion"] = "GUARDAR"
        context["accion2"] = "CANCELAR"
        context["accion2_url"] = reverse_lazy("activos:lista_activos")
        context["activate"] = True
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        usuario = self.request.user
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)

        if form.is_valid() and form2.is_valid():
            codigo = form2.cleaned_data.get("codigo")

            if Activo.objects.filter(codigo=codigo).exists():
                messages.error(request, "El código ya existe, por favor ingrese otro código.")
                return self.render_to_response(self.get_context_data(form=form, form2=form2))

            try:
                responsable = form.cleaned_data.get("responsable")
                piso_ubicacion = form.cleaned_data.get("piso_ubicacion")
                oficina_ubicacion = form.cleaned_data.get("oficina_ubicacion")
                form2.save()
                activos = Activo.objects.get(codigo=codigo)
                activo_responsable = form.save(commit=False)
                activo_responsable.activo = activos
                activo_responsable.save()
                activos_responsable = Activo_responsable.objects.get(activo=activos)
                Line_Activo_Responsable.objects.create(
                    slug=activos_responsable.slug,
                    responsable=responsable,
                    piso_ubicacion=piso_ubicacion,
                    oficina_ubicacion=oficina_ubicacion,
                    observacion="Se registró los datos del activo y del responsable",
                    creador=usuario,
                )
                messages.success(request, "El activo con responsable fue registrado correctamente.")
                return HttpResponseRedirect(reverse("activos:lista_activos"))

            except IntegrityError:
                messages.error(request,"Ocurrió un error al registrar el activo. Verifique los datos e intente nuevamente.",)
                return self.render_to_response(self.get_context_data(form=form, form2=form2))

        else:
            messages.error(request, " Por favor complete todos los campos correctamente." )
            return self.render_to_response(self.get_context_data(form=form, form2=form2))


class ActualizarActivoResponsable(LoginRequiredMixin, UpdateView):
    model = Activo_responsable
    second_model = Activo
    template_name = "RegistroActualizacion/activo.html"
    form_class = R_Activo_responsable
    second_form_class = A_Activo
    success_url = reverse_lazy("activos:lista_activos")

    def get_object(self, queryset=None):
        return Activo_responsable.objects.get(slug=self.kwargs["slug"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        activo_responsable = self.get_object()
        activo = activo_responsable.activo

        context["form"] = kwargs.get(
            "form", self.form_class(instance=activo_responsable)
        )
        context["form2"] = kwargs.get("form2", self.second_form_class(instance=activo))

        context["titulo"] = "ACTUALIZACIÓN DE INFORMACIÓN DE ACTIVO Y RESPONSABLE"
        context["subtitulo_1"] = "DATOS DEL RESPONSABLE, UBICACION Y ESTADO DEL ACTIVO"
        context["subtitulo_2"] = "DATOS DEL ACTIVO"
        context["accion"] = "ACTUALIZAR"
        context["accion2"] = "CANCELAR"
        context["accion2_url"] = reverse_lazy("activos:lista_activos")
        context["activate"] = True
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        usuario = self.request.user
        activo_responsable = self.object
        activo = activo_responsable.activo
        old_responsable = activo_responsable.responsable
        old_piso = activo_responsable.piso_ubicacion
        old_oficina = activo_responsable.oficina_ubicacion
        old_estado = activo_responsable.estado

        form = self.form_class(request.POST, instance=activo_responsable)
        form2 = self.second_form_class(request.POST, instance=activo)

        if form.is_valid() and form2.is_valid():
            form2.save()
            form.save()
            nuevo_responsable = activo_responsable.responsable
            nuevo_piso = activo_responsable.piso_ubicacion
            nuevo_oficina = activo_responsable.oficina_ubicacion
            nuevo_estado = activo_responsable.estado
            cambios = []
            if old_responsable != nuevo_responsable:
                cambios.append(
                    f"Responsable cambiado: antes era '{old_responsable or ''}', ahora es '{nuevo_responsable or ''}'"
                )
            if old_piso != nuevo_piso:
                cambios.append(
                    f"Ubicacion cambiada: antes era '{old_piso or ''}', ahora es '{nuevo_piso or ''}'"
                )
            if old_oficina != nuevo_oficina:
                cambios.append(
                    f"Ubicacion cambiad: antes era '{old_oficina or ''}', ahora es '{nuevo_oficina or ''}'"
                )
            if old_estado != nuevo_estado:
                cambios.append(
                    f"Estado cambiado: antes era '{old_estado or ''}', ahora es '{nuevo_estado or ''}'"
                )

            if cambios:
                observacion = "Se actualizó la información del " + ", ".join(cambios)
            else:
                observacion = "No se realizaron cambios relevantes"

            Line_Activo_Responsable.objects.create(
                slug=activo_responsable.slug,
                responsable=nuevo_responsable,
                piso_ubicacion=nuevo_piso,
                oficina_ubicacion=nuevo_oficina,
                estado=nuevo_estado,
                observacion=observacion,
                creador=usuario,
            )

            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(
                self.get_context_data(form=form, form2=form2)
            )

@login_required
@require_http_methods(["GET", "POST"])
def ajax_r_activo(request):
    data = {}
    if request.method == "POST":
        form = R_Activo(request.POST)
        if form.is_valid():
            try:
                activo = form.save()
                new_slug = str(uuid.uuid4())
                current_datetime = timezone.now()
                Activo_responsable.objects.create(
                    activo=activo,
                    slug=new_slug,
                    fecha_registro=current_datetime,
                    estado="Bueno",
                    responsable=None, 
                    piso_ubicacion="ALMACENES",
                    oficina_ubicacion="ALMACEN",
                )
                data["form_is_valid"] = True
            except Exception as e:               
                try:
                    activo.delete()
                except:
                    pass

                data["form_is_valid"] = False
                data["error_message"] = (
                    f"Error al registrar Activo_responsable: {str(e)}"
                )

        else:
            data["form_is_valid"] = False
    return JsonResponse(data)


@login_required
@require_http_methods(["GET", "POST"])
def ajax_r_activo_responsable(request):
    data = {}
    if request.method == "POST":
        f_resp = R_Activo_responsable(request.POST)
        f_act = R_Activo(request.POST)
        if f_resp.is_valid() and f_act.is_valid():
            activo = f_act.save()
            obj = f_resp.save(commit=False)
            obj.activo = activo
            obj.save()
            data["form_is_valid"] = True
        else:
            data["form_is_valid"] = False
    else:
        f_resp = R_Activo_responsable()
        f_act = R_Activo()

    context = {
        "form": f_resp,
        "form2": f_act,
        "titulo": "REGISTRO ACTIVO + RESPONSABLE",
    }
    data["html_form"] = render_to_string(
        "RegistroActualizacion/model_activo_responsable.html", context, request=request
    )
    return JsonResponse(data)


