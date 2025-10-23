from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import ObjectDoesNotExist, Q
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
    HttpResponseServerError,
)
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateformat import format as dj_format
from django.views.generic import (
    CreateView,
    View,
    ListView,
    UpdateView,
    TemplateView,
)

from activos.forms import A_Activo_responsable
from activos.models import Activo
from designacion.models import Activo_responsable, Line_Activo_Responsable
from revision.forms import R_Revision, A_Revision_P, R_Revision_ACtivo
from revision.models import Revision, Revision_line, Revision_Activo
from users.models import User, Personal


def get_menu_context(request):
    data = {}
    data["mostrar_menu_registro_encargado"] = False
    data["revision_activa"] = None

    if not request.user.is_authenticated:
        return data

    try:
        revision_activa = Revision.objects.get(estado=True)
        data["revision_activa"] = revision_activa
        personal_del_usuario = Personal.objects.get(user=request.user)

        if revision_activa.revisores.filter(pk=personal_del_usuario.pk).exists():
            data["mostrar_menu_registro_encargado"] = True

    except Revision.DoesNotExist:
        pass
    except ObjectDoesNotExist:
        pass

    return data


class MenuContextMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        return context


class RegistroRevisionActivoView(LoginRequiredMixin, MenuContextMixin, TemplateView):
    template_name = "RegistroActualizacion/Revision_Activo/formulario.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            revision_activa = Revision.objects.get(estado=True)
            context["slug"] = revision_activa.slug
        except Revision.DoesNotExist:
            context["slug"] = None
        except Revision.MultipleObjectsReturned:
            context["slug"] = Revision.objects.filter(estado=True).first().slug
        return context


class ListaCambiosRevision(LoginRequiredMixin, ListView):
    model = Revision_line
    template_name = "lista/revision_line.html"

    def get_context_data(self, **kwargs):
        context = super(ListaCambiosRevision, self).get_context_data(**kwargs)
        slug = self.kwargs.get("slug", None)
        context["titulo"] = "LISTA DE CAMBIOS DE ACTIVOS"
        context["object_list"] = self.model.objects.filter(
            revision__slug=slug
        ).order_by("-fecha_creacion")
        return context


class ListaRevisiones(LoginRequiredMixin, ListView):
    model = Revision
    template_name = "lista/revision.html"

    def get_queryset(self):
        user = self.request.user

        if (
            user.is_superuser or user.is_encargado
        ):  # Asumiendo que is_encargado está en el objeto User
            # Si no tienes is_encargado en el modelo User, usa:
            # try: return self.model.objects.all() if Personal.objects.get(user=user).is_encargado else self._filter_revisores(user)
            return self.model.objects.all()

        # 2. Lógica para Personal/Revisores (solo ve asignadas)
        else:
            return self._filter_revisores(user)  # Llama a la lógica de filtrado

    # ⚠️ FUNCIÓN AUXILIAR PARA CLARIDAD Y REUSO
    def _filter_revisores(self, user):
        try:
            # Obtener la instancia del Personal asociada al usuario logueado
            personal_instance = Personal.objects.get(user=user)
        except ObjectDoesNotExist:
            # Si no tiene perfil Personal, no debe ver nada
            return self.model.objects.none()

        queryset = self.model.objects.filter(
            # Usa Q() para combinar OR: Revisor O Encargado de la revisión
            Q(revisores=personal_instance)
            | Q(encargado=personal_instance)
        ).distinct()

        return queryset

    # 2. Mantenemos el get_context_data original
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["titulo"] = "LISTA DE REVISIONES DE ACTIVOS"

        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        context["entity_registro_nom"] = "REGISTRAR NUEVA REVISION"
        context["entity_registro"] = reverse_lazy("revision:ajax_r_Revision", args=[])

        # ⚠️ IMPORTANTE: Aquí se consulta una variable de CONTEXTO, no la lista principal.
        # Si 'revision' fuera la lista principal, anularía el filtro de get_queryset.
        revision = Revision.objects.filter(estado=True)
        if revision:
            revision_datos = revision.first()
            context["revisionr"] = revision
            context["revision_datos"] = revision_datos

        return context


def ajax_r_Revision(request):
    data = dict()
    try:
        if request.method == "POST":
            form = R_Revision(request.POST)
            usuario = request.user
            try:
                personal_d = Personal.objects.get(user=usuario)
            except Personal.DoesNotExist:
                data["form_is_valid"] = False
                data["html_form"] = (
                    "<p class='text-danger'>El usuario no tiene asignado un perfil Personal.</p>"
                )
                return JsonResponse(data)

            if form.is_valid():
                revision = form.save(commit=False)
                revision.encargado = personal_d
                revision.save()

                form.save_m2m()

                revisores = revision.revisores.all()
                for revisor in revisores:
                    p_revisores = revisor.user.id
                    user_revisores = User.objects.get(id=p_revisores)
                    user_revisores.is_revisor = True
                    user_revisores.save()

                if revision.estado == None:
                    estado = "Sin Accion"

                Revision_line.objects.create(
                    revision=revision,
                    estado=estado,
                    creador=usuario,
                    observacion="Se registró la Revisión",
                )
                data["form_is_valid"] = True
            else:
                data["form_is_valid"] = False
        else:
            form = R_Revision()

        context = {"form": form, "titulo": "Registrar Revisión"}
        data["html_form"] = render_to_string(
            "RegistroActualizacion/model_revision.html", context, request=request
        )
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e), "form_is_valid": False}, status=500)


def ajax_editar_revision(request, slug):
    data = dict()
    try:
        revision = get_object_or_404(Revision, slug=slug)
        usuario = request.user
        if usuario.is_superuser:
            old_motivo = revision.motivo
            old_nombre = revision.nombre
            old_descripcion = revision.descripcion
        old_revisores = revision.revisores
        revisores = revision.revisores.all()
        for revisor in revisores:
            p_revisores = revisor.user.id
            user_revisores = User.objects.get(id=p_revisores)
            user_revisores.is_revisor = False
            user_revisores.save()
        if request.method == "POST":
            if usuario.is_superuser:
                form = R_Revision(request.POST, instance=revision)
            elif usuario.is_encargado:
                form = A_Revision_P(request.POST, instance=revision)
            if form.is_valid():
                revision_form = form.save(commit=False)
                revision_form.save()
                form.save_m2m()
                if usuario.is_superuser:
                    new_motivo = revision.motivo
                    new_nombre = revision.nombre
                    new_descripcion = revision.descripcion
                new_revisores = revision.revisores
                cambios = []
                if usuario.is_superuser:
                    if (old_motivo or "") != (new_motivo or ""):
                        cambios.append(
                            f"Motivo cambiado: antes era '{old_motivo or ''}', ahora es '{new_motivo or ''}'"
                        )
                    if (old_nombre or "") != (new_nombre or ""):
                        cambios.append(
                            f"Nombre cambiado: antes era '{old_nombre or ''}', ahora es '{new_nombre or ''}'"
                        )
                    if (old_descripcion or "") != (new_descripcion or ""):
                        cambios.append(
                            f"Descripcion cambiado: antes era '{old_descripcion or ''}', ahora es '{new_descripcion or ''}'"
                        )
                if (old_revisores or "") != (new_revisores or ""):
                    cambios.append(
                        f"Revisores cambiado: antes era '{old_revisores or ''}', ahora es '{new_revisores or ''}'"
                    )
                if cambios:
                    observacion = "Se actualizó la información del " + ", ".join(
                        cambios
                    )
                else:
                    observacion = "No se realizaron cambios relevantes"
                data["form_is_valid"] = True
                for revisor in revisores:
                    p_revisores = revisor.user.id
                    user_revisores = User.objects.get(id=p_revisores)
                    user_revisores.is_revisor = True
                    user_revisores.save()
                if revision.estado == None:
                    estado = "Sin Accion"
                elif revision.estado:
                    estado = "En Curso"
                elif not revision.estado:
                    estado = "Finalizado"
                Revision_line.objects.create(
                    revision=revision,
                    estado=estado,
                    creador=usuario,
                    observacion=observacion,
                )
                data["html_row"] = render_to_string(
                    "lista/revision.html", {"revision": revision}, request=request
                )
            else:
                data["form_is_valid"] = False
        else:
            if usuario.is_superuser:
                form = R_Revision(instance=revision)
            elif usuario.is_encargado:
                form = A_Revision_P(instance=revision)
        context = {"form": form, "titulo": "Editar Revisión"}
        data["html_form"] = render_to_string(
            "RegistroActualizacion/model_revision.html", context, request=request
        )
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def inicio_fin_Revision(request, slug):
    data3 = {}
    usuario = request.user
    try:
        revision = get_object_or_404(Revision, slug=slug)

        if revision.fechaHora_inicio is None:
            revision.fechaHora_inicio = timezone.now()
            revision.estado = True
            revision.save()
            Revision_line.objects.create(
                revision=revision,
                estado="Iniciada",
                creador=usuario,
                observacion="Se inicia el proceso de revision",
            )
            data3["status"] = "iniciada"
            data3["fechaHora_inicio"] = revision.fechaHora_inicio.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        elif (
            revision.fechaHora_finalizacion is None
            and revision.fechaHora_inicio is not None
        ):
            revision.fechaHora_finalizacion = timezone.now()
            revision.estado = False
            revision.save()
            Revision_line.objects.create(
                revision=revision,
                estado="Finalizada",
                creador=usuario,
                observacion="Se Finaliza el proceso de revision",
            )
            data3["status"] = "finalizada"
            data3["fechaHora_finalizacion"] = revision.fechaHora_finalizacion.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            data3["status"] = "ya_finalizada"
        return JsonResponse(data3)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def ajax_ver_revision(request, slug):
    try:
        revision = get_object_or_404(Revision, slug=slug)
        usuario = request.user
        data = {
            "html_form": render_to_string(
                "Visualizar/revision.html", {"revision": revision}, request=request
            )
        }
        Revision_line.objects.create(
            revision=revision,
            estado="Ver",
            creador=usuario,
            observacion="Se reviso los datos del proceso de revision",
        )
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


class Revision_RActivos(LoginRequiredMixin, TemplateView):
    template_name = "RegistroActualizacion/Revision_activo/formulario.html"

    def get_context_data(self, **kwargs):
        context = super(Revision_RActivos, self).get_context_data(**kwargs)
        slug = self.kwargs.get("slug", None)
        revision = get_object_or_404(Revision, slug=slug)
        revisonActivo = Revision_Activo.objects.filter(revision__slug=revision.slug)
        context["titulo"] = "REGISTRO DE REVISION DE ACTIVO"
        context["object_list"] = revisonActivo
        context["slug"] = slug
        return context


def buscar_activo(request, slug):
    if request.method == "POST":
        codigo = request.POST.get("codigo")

        if not codigo:
            return HttpResponse("Código no proporcionado", status=400)
        TEMPLATE_BASE_PATH = "RegistroActualizacion/Revision_Activo/"

        try:
            activo = get_object_or_404(Activo, codigo=codigo)
            revision = get_object_or_404(Revision, slug=slug, estado=True)
            activo_resp = get_object_or_404(Activo_responsable, activo=activo)
            try:
                revision_activo = Revision_Activo.objects.get(
                    revision=revision, activo_res=activo_resp
                )
                context = {
                    "activo": activo,
                    "revision": revision_activo,
                    "titulo": "Activo ya revisado",
                }
                html = render_to_string(
                    TEMPLATE_BASE_PATH + "modal_ya_revisado.html",
                    context,
                    request=request,
                )

            except Revision_Activo.DoesNotExist:
                form = R_Revision_ACtivo()
                context = {
                    "activo": activo,
                    "slug": slug,
                    "form": form,
                    "titulo": "OBSERVACIÓN DE LA REVISIÓN",
                }
                html = render_to_string(
                    TEMPLATE_BASE_PATH + "modal_form.html", context, request=request
                )

            return HttpResponse(html)
          
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Activo, Revisión o Responsable no encontrado.")

        except Exception as e:
            print(f"Error interno inesperado en buscar_activo: {e}")
            return HttpResponseServerError(f"Error interno inesperado: {e}")

    return HttpResponse("Método no permitido", status=405)


def actualizar_activo(request, slug, codigo):
    user = request.user
    personal_user = User.objects.get(username=user)
    personal = Personal.objects.get(user=personal_user)
    print(request.method)
    if request.method == "POST":
        print(codigo, "codigo")
        activo = Activo.objects.get(codigo=codigo)
        activo_resp = Activo_responsable.objects.get(activo__codigo=activo.codigo)
        old_piso = activo_resp.piso_ubicacion
        old_oficina = activo_resp.oficina_ubicacion
        revision = Revision.objects.get(slug=slug)

        form = R_Revision_ACtivo(request.POST)
        form2 = A_Activo_responsable(request.POST, instance=activo_resp)

        if form.is_valid() and form2.is_valid():
            form2.save()
            new_piso = activo_resp.piso_ubicacion
            new_oficina = activo_resp.oficina_ubicacion
            cambios = []

            if old_oficina != new_oficina:
                cambios.append(
                    f"Oficina cambiada: antes era '{old_oficina or ''}', ahora es '{new_oficina or ''}'"
                )
            if old_piso != new_piso:
                cambios.append(
                    f"Piso cambiado: antes era '{old_piso or ''}', ahora es '{new_piso or ''}'"
                )

            if cambios:
                Line_Activo_Responsable.objects.create(
                    slug=activo_resp.slug,
                    responsable=activo_resp.responsable,
                    piso_ubicacion=activo_resp.piso_ubicacion,
                    oficina_ubicacion=activo_resp.oficina_ubicacion,
                    observacion=cambios,
                    creador=user,
                )

            revision_activo = form.save(commit=False)
            revision_activo.revision = revision
            revision_activo.activo_res = activo_resp
            revision_activo.estado = True
            revision_activo.encargado = personal_user
            revision_activo.save()

            return redirect("revision:revision_activo", slug=slug)

    return HttpResponseNotAllowed(["POST"])


class ListaCompletaRevision_Activo(LoginRequiredMixin, ListView):
    model = Revision_Activo
    template_name = "lista/activo_revision.html"

    def get_context_data(self, **kwargs):
        context = super(ListaCompletaRevision_Activo, self).get_context_data(**kwargs)
        slug = self.kwargs.get("slug", None)
        context["titulo"] = "LISTA DE REVISION DE ACTIVOS"
        context["object_list"] = self.model.objects.filter(slug=slug)
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        context["entity_registro_nom"] = "REGISTRAR NUEVA REVISION"
        context["entity_registro"] = reverse_lazy("revision:ajax_r_Revision", args=[])
        revision = Revision.objects.filter(estado=True)
        if revision:
            revision_datos = revision.first()
            context["revision"] = revision
            context["revision_datos"] = revision_datos
        return context
