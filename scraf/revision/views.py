from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

from revision.models import Revision, Revision_line
from users.models import User, Personal

from revision.forms import R_Revision
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
        context['entity_registro'] = reverse_lazy('revision:registro_revisiones', args=[])
        context['entity_registro_nom'] = 'REGISTRAR NUEVA REVISION'
            
        return context

class RegistroRevisiones(LoginRequiredMixin, CreateView):
    model = Revision
    template_name = 'RegistroActualizacion/revision.html'
    form_class = R_Revision
    success_url = reverse_lazy('revision:lista_revisiones')
    
    def get_context_data(self, **kwargs):
        context = super(RegistroRevisiones, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        context['titulo'] = 'REGISTRO DE REVISIONES DE ACTIVOS FIJOS'
        context['accion'] = 'GUARDAR'
        context['accion2'] = 'CANCELAR'
        context['accion2_url'] = reverse_lazy('revision:lista_revisiones')
        return context
    
    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        usuario_d = User.objects.get(username=usuario)
        personal_d = Personal.objects.get(user=usuario_d)
        form = self.form_class(request.POST)
        if form.is_valid():
            self.object = form.save(commit=False)  # ← Esto crea self.object correctamente
            self.object.encargado = personal_d
            self.object.save()
            form.save_m2m()

            Revision_line.objects.create(
                slug=self.object.slug,
                revision=self.object,
                estado=self.object.estado,
                creador=usuario,
                observacion='Se registró una nueva Revisión'
            )

            return HttpResponseRedirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))