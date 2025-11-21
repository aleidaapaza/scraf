from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView,TemplateView
from django.template.loader import render_to_string
from django.db.models import ObjectDoesNotExist, Q

from django.shortcuts import (
    redirect,
    get_object_or_404,
)
from django.http import (
    HttpResponse,
    JsonResponse,
    HttpResponseNotAllowed,
    HttpResponseNotFound,
    HttpResponseServerError,
)

from users.models import Persona, Personal, User
from activos.models import Activo
from designacion.models import Activo_responsable, Line_Activo_Responsable
from revision.models import Revision, Revision_Activo

from revision.views import get_menu_context

from revision.forms import R_Revision_activo_observado
from activos.forms import A_Activo_responsable

class Revision_ActivosObservados(LoginRequiredMixin, TemplateView):
    template_name = "RegistroActualizacion/Revision_activo/formulario.html"

    def get_context_data(self, **kwargs):
        context = super(Revision_ActivosObservados, self).get_context_data(**kwargs)
        context.update(get_menu_context(self.request))
        slug = self.kwargs.get("slug", None)
        revision = get_object_or_404(Revision, slug=slug)
        revisonActivo = Revision_Activo.objects.filter(revision__slug=revision.slug, estado=True)
        context["titulo"] = f'REVISION DE ACTIVOS FALTANTES DE LA REVISION {slug}'
        context["instruccion"] = f'Ingresa el código del activo observado'
        context["object_list"] = revisonActivo
        context["slug"] = slug
        context["observado"] = True
        context["observado_cant"] = revisonActivo.count()

        return context

def buscar_activo_obs(request, slug):
    if request.method == "POST":
        codigo = request.POST.get("codigo")

        if not codigo:
            return HttpResponse("Código no proporcionado", status=400)
        
        TEMPLATE_BASE_PATH = "RegistroActualizacion/Revision_Activo/"

        try:
            activo = get_object_or_404(Activo, codigo=codigo)
            revision = get_object_or_404(Revision, slug=slug, estado=True)
            activo_resp = get_object_or_404(Activo_responsable, activo=activo)
            revision_activo = Revision_Activo.objects.filter(revision=revision, activo=activo, estado = False)
            revision_activo_T = Revision_Activo.objects.filter(revision=revision, activo=activo, estado = True)
            if revision_activo:
                context = {
                    "activo": activo,
                    "revision": revision_activo.first(),
                    "titulo": "Activo ya revisado",
                }
                html = render_to_string(
                    TEMPLATE_BASE_PATH + "modal_ya_revisado.html",
                    context,
                    request=request,
                )

            elif revision_activo_T:
                revision_activo_TR =revision_activo_T.first()
                form = R_Revision_activo_observado()
                form2 = A_Activo_responsable(instance=activo_resp)
                context = {
                    "activo": activo,
                    "slug": slug,
                    "form": form,
                    "form2": form2,
                    "titulo": "OBSERVACIÓN DE LA REVISIÓN",
                }
                html = render_to_string(
                    TEMPLATE_BASE_PATH + "modal_form2.html", context, request=request
                )
            return HttpResponse(html)
          
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Activo, Revisión o Responsable no encontrado.")

        except Exception as e:
            return HttpResponseServerError(f"Error interno inesperado: {e}")

    return HttpResponse("Método no permitido", status=405)


def actualizar_activo_obs(request, slug, codigo):
    user = request.user
    personal_user = User.objects.get(username=user)
    personal = Personal.objects.get(user=personal_user)
    if request.method == "POST":
        activo = Activo.objects.get(codigo=codigo)
        activo_resp = Activo_responsable.objects.get(activo__codigo=activo.codigo)
        revision = Revision.objects.get(slug=slug)
        revision_Activo = Revision_Activo.objects.get(revision=revision, activo=activo,)

        old_Observacion = revision_Activo.observacion
        old_piso = activo_resp.piso_ubicacion
        old_oficina = activo_resp.oficina_ubicacion

        form = R_Revision_activo_observado(request.POST, instance = revision_Activo)
        form2 = A_Activo_responsable(request.POST, instance=activo_resp)

        if form.is_valid() and form2.is_valid():
            form2.save()
            new_piso = activo_resp.piso_ubicacion
            new_oficina = activo_resp.oficina_ubicacion
            cambios = []
            if old_oficina != new_oficina:
                cambios.append(
                    f"Oficina cambiada: antes se encontraba en '{old_oficina or ''}', ahora esta en '{new_oficina or ''}'"
                )
            if old_piso != new_piso:
                cambios.append(
                    f"Piso cambiado: antes se encontraba en '{old_piso or ''}', ahora esta enc '{new_piso or ''}'"
                )

            observacion = form.cleaned_data.get("observacion")
            observacion_nueva = f"""
                {old_Observacion}
                {revision_Activo.encargado}
                ------------------------
                {observacion}
                """
            if cambios:
                Line_Activo_Responsable.objects.create(
                    slug=activo,
                    creador=request.user,
                    responsable=activo_resp.responsable,
                    piso_ubicacion=new_piso,
                    oficina_ubicacion=new_oficina,
                    estado = activo.estadoActivo,
                    observacion=f"""
                        {cambios}
                        ------------------------
                        Se subsano la Observacion de la revision del activo
                        """
                )
            revision_Activo.encargado = request.user
            revision_Activo.observacion = observacion_nueva
            revision_Activo.estado = False
            revision_Activo.save()

            return redirect("revision:revision_activo_observado", slug=slug)

    return HttpResponseNotAllowed(["POST"])

