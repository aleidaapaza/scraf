import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView

from activos.forms import R_Activo, R_Activo_responsable, A_Activo, ActivoForm
from activos.models import Activo, AuxiliarContable, Line_Activo
from designacion.models import Activo_responsable, Line_Activo_Responsable
from revision.views import get_menu_context
from users.models import User


class ListaActivos(LoginRequiredMixin, ListView):
    model = Activo
    template_name = "lista/activo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "LISTA DE ACTIVOS EN LA INSTITUCION"
        context["object_list"] = self.model.objects.all()
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        context.update(get_menu_context(self.request))
        if usuario_d.g_Activos:
            context["entity_registro"] = reverse_lazy("activos:ajax_r_activo")
            context["entity_registro"] = reverse_lazy(
                "activos:registro_activos", args=[]
            )
            context["entity_registro_nom"] = "REGISTRAR NUEVO ACTIVO"
            context["entity_registro2"] = reverse_lazy("activos:ajax_r_activo_resp")
            context["entity_registro_nom2"] = "REGISTRAR NUEVO ACTIVO CON RESPONSABLE"
        return context


class RegistroActivo(LoginRequiredMixin, CreateView):
    model = Activo
    template_name = "RegistroActualizacion/activo.html"
    form_class = ActivoForm
    success_url = reverse_lazy("activos:lista_activos")
    def get_context_data(self, **kwargs):
        context = super(RegistroActivo, self).get_context_data(**kwargs)
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
            print(activo)
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
        # Aplicar filtro de búsqueda si existe
        if search_term:
            auxiliares = auxiliares.filter(nombre__icontains=search_term)
        # Formatear datos para Select2
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
            slug = self.kwargs.get("slug")
            activo_line = Line_Activo_Responsable.objects.filter(slug=slug).order_by("-fecha_registro")
            activo_responsable_line = Line_Activo_Responsable.objects.filter(slug=slug).order_by("-fecha_registro")
            context["titulo"] = "INFORMACION DEL ACTIVO"
            context["activo"] = activo
            context["line"] = activo_line
            return context

class VerActivo(LoginRequiredMixin, TemplateView):
    template_name = "Visualizar/activo.html"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        activo = Activo_responsable.objects.get(slug=slug)
        activo_line = Line_Activo_Responsable.objects.filter(slug=slug).order_by("-fecha_registro")
        context["titulo"] = "INFORMACION DEL ACTIVO"
        context["activo"] = activo
        context["line"] = activo_line
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

            # ✅ Verificamos si ya existe un activo con ese código
            if Activo.objects.filter(codigo=codigo).exists():
                messages.error(
                    request, "⚠️ El código ya existe, por favor ingrese otro código."
                )
                return self.render_to_response(
                    self.get_context_data(form=form, form2=form2)
                )

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
                messages.success(
                    request,
                    "✅ El activo con responsable fue registrado correctamente.",
                )
                return HttpResponseRedirect(reverse("activos:lista_activos"))

            except IntegrityError:
                messages.error(
                    request,
                    "⚠️ Ocurrió un error al registrar el activo. Verifique los datos e intente nuevamente.",
                )
                return self.render_to_response(
                    self.get_context_data(form=form, form2=form2)
                )

        else:
            messages.error(
                request, "⚠️ Por favor complete todos los campos correctamente."
            )
            return self.render_to_response(
                self.get_context_data(form=form, form2=form2)
            )


class VerActivo(LoginRequiredMixin, TemplateView):
    template_name = "Visualizar/activo.html"
    def get_context_data(self, **kwargs):
        context = super(VerActivo, self).get_context_data(**kwargs)
        slug = self.kwargs.get("slug", None)
        activo = Activo_responsable.objects.get(slug=slug)
        activo_line = Line_Activo_Responsable.objects.filter(slug=slug).order_by("-fecha_registro")
        context["titulo"] = "INFORMACION DEL ACTIVO"
        context["activo"] = activo
        context["line"] = activo_line
        return context


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

from django.utils import timezone
import uuid

@login_required
@require_http_methods(["GET", "POST"])
def ajax_r_activo(request):
    data = {}
    if request.method == "POST":
        form = R_Activo(request.POST)
        if form.is_valid():

            try:
                # 1. Guardar el Activo
                activo = form.save()

                # 2. Generar campos obligatorios
                new_slug = str(uuid.uuid4())
                current_datetime = timezone.now()

                # 3. ⚠️ CREAR ACTIVO_RESPONSABLE MÍNIMO (Almacén)
                Activo_responsable.objects.create(
                    activo=activo,
                    slug=new_slug,  # <-- Obligatorio
                    fecha_registro=current_datetime,  # <-- Obligatorio
                    # ⚠️ CAMBIO CRÍTICO: INCLUIR ESTADO
                    estado="Bueno",  # <-- Asumiendo que es el valor inicial ("Bueno")
                    responsable=None,  # <-- Nulo, ya que no tiene responsable
                    piso_ubicacion="ALMACENES",
                    oficina_ubicacion="ALMACEN",
                )

                data["form_is_valid"] = True

            except Exception as e:
                # Si falla, devolvemos el error y eliminamos el Activo huérfano.
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

    # ... (el resto del código de la función) ...
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


