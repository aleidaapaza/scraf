from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404

from revision.models import Revision, Revision_line
from users.models import User, Personal

from revision.forms import R_Revision, A_Revision_P
# Create your views here.

class ListaRevisiones(LoginRequiredMixin, ListView):
    model = Revision
    template_name = 'lista/revision.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'LISTA DE REVISIONES DE ACTIVOS'
        context['object_list'] = self.model.objects.all()
        usuario = self.request.user
        usuario_d = User.objects.get(username = usuario)
        context['entity_registro_nom'] = 'REGISTRAR NUEVA REVISION'
        context['entity_registro'] = reverse_lazy('revision:ajax_r_Revision', args=[])
            
        return context

def ajax_r_Revision(request):
    data = dict()
    if request.method == 'POST':
        form = R_Revision(request.POST)
        usuario = request.user
        try:
            personal_d = Personal.objects.get(user=usuario)
        except Personal.DoesNotExist:
            data['form_is_valid'] = False
            data['html_form'] = "<p class='text-danger'>El usuario no tiene asignado un perfil Personal.</p>"
            return JsonResponse(data)

        if form.is_valid():
            revision = form.save(commit=False)
            revision.encargado = personal_d
            revision.save()
            form.save_m2m()

            Revision_line.objects.create(
                slug=revision.slug,
                revision=revision,
                estado=revision.estado,
                creador=usuario,
                observacion='Se registró la Revisión'
            )

            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = R_Revision()

    context = {
        'form': form,
        'titulo': 'Registrar Revisión'
    }

    data['html_form'] = render_to_string('RegistroActualizacion/model_revision.html', context, request=request)
    return JsonResponse(data)

def ajax_editar_revision(request, slug):
    data = dict()
    revision = get_object_or_404(Revision, slug=slug)
    usuario = request.user
    if usuario.is_superuser:
        old_motivo = revision.motivo
        old_nombre = revision.nombre
        old_descripcion = revision.descripcion
    old_revisores = revision.revisores    
    if request.method == 'POST':
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
                if (old_motivo or '') != (new_motivo or ''):
                    cambios.append(f"Motivo cambiado: antes era '{old_motivo or ''}', ahora es '{new_motivo or ''}'")
                if (old_nombre or '') != (new_nombre or ''):
                    cambios.append(f"Nombre cambiado: antes era '{old_nombre or ''}', ahora es '{new_nombre or ''}'")
                if (old_descripcion or '') != (new_descripcion or ''):
                    cambios.append(f"Descripcion cambiado: antes era '{old_descripcion or ''}', ahora es '{new_descripcion or ''}'")
            if (old_revisores or '') != (new_revisores or ''):
                cambios.append(f"Revisores cambiado: antes era '{old_revisores or ''}', ahora es '{new_revisores or ''}'")
            
            if cambios:
                observacion = "Se actualizó la información del " + ", ".join(cambios)
            else:
                observacion = "No se realizaron cambios relevantes"

            data['form_is_valid'] = True
            Revision_line.objects.create(
                slug=revision.slug,
                revision=revision,
                estado=revision.estado,
                creador=usuario,
                observacion=observacion
            )
            # Actualizar solo la fila correspondiente en la tabla (opcional)
            data['html_row'] = render_to_string(
                'lista/revision.html',
                {'revision': revision},
                request=request
            )
        else:
            data['form_is_valid'] = False
    else:
        if usuario.is_superuser:
            form = R_Revision(instance=revision)
        elif usuario.is_encargado:
            form = A_Revision_P(instance=revision)
    context = {
        'form': form,
        'titulo': 'Editar Revisión'
    }

    data['html_form'] = render_to_string(
        'RegistroActualizacion/model_revision.html',  # puedes usar el mismo que para crear
        context,
        request=request
    )
    return JsonResponse(data)