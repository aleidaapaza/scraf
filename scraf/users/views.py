from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

from users.models import Personal, Persona, User
from users.forms import R_User, R_Persona, A_User, A_Personal
# Create your views here.

class ListaPersonal(LoginRequiredMixin, ListView):
    model = Personal
    template_name = 'lista/personal.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['superuser']=True
        context['titulo'] = 'LISTA DE PERSONAL'
        context['object_list'] = self.model.objects.all()
        context['entity_registro'] = reverse_lazy('users:registro_personal', args=[])
        context['entity_registro_nom'] = 'REGISTRAR PERSONAL'
        return context
    
class RegistroPersonal(LoginRequiredMixin, CreateView):
    model = Personal
    template_name = 'RegistroActualizacion/personal.html'
    form_class = R_Persona
    second_form_class = R_User
    success_url = reverse_lazy('user:lista_personal')

    def get_context_data(self, **kwargs):
        context = super(RegistroPersonal, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(self.request.GET)
        context['superuser']=True
        context['form'] = self.form_class(self.request.GET)
        context['form2'] = self.second_form_class(self.request.GET)      
        context['titulo'] = 'REGISTRO DE PERSONAL'
        context['accion'] = 'GUARDAR'
        context['accion2'] = 'CANCELAR'
        context['accion2_url'] = reverse_lazy('user:lista_personal')
        context['activate'] = True
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)

        if form.is_valid() and form2.is_valid():
            carnet = form.cleaned_data.get('carnet')

            usuario = form2.save(commit=False)
            usuario.is_personal = True
            usuario.password = f'{carnet}'
            usuario.set_password(usuario.password)
            rol_rev = request.POST.get('rol_revision', '')
            usuario.is_encargado = (rol_rev == 'encargado')
            usuario.is_revisor   = (rol_rev == 'apoyo')

            rol_act = request.POST.get('rol_activos', '')
            usuario.g_personal  = (rol_act == 'personal')
            usuario.g_Activos   = (rol_act == 'gestion_activos')
            usuario.v_Activos   = (rol_act == 'solo_visualiza')

            usuario.save()
            persona = form.save()
            Personal.objects.create(persona=persona, user=usuario)

            return HttpResponseRedirect(reverse('users:lista_personal', args=[]))
        else:
            self.object = None
            return self.render_to_response(self.get_context_data(form=form, form2=form2))



class ActualizacionPersonal(LoginRequiredMixin, UpdateView):
    model = Personal
    second_model = User 
    third_model = Persona
    template_name = 'RegistroActualizacion/personal_a.html'
    form_class = A_Personal
    second_form_class = A_User
    third_form_class = R_Persona

    def get_context_data(self, **kwargs):
        context = super(ActualizacionPersonal, self).get_context_data(**kwargs)
        slug = self.kwargs.get('slug', None)        
        personal_p = self.model.objects.get(slug=slug)
        user_p = self.second_model.objects.get(id=personal_p.user.pk)
        persona_p = self.third_model.objects.get(id=personal_p.persona.pk)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(instance=user_p)
        if 'form3' not in context:
            context['form3'] = self.third_form_class(instance=persona_p)
        context['titulo'] = 'ACTUALIZAR DATOS DEL PERSONAL'
        context['accion2'] = 'Cancelar'
        context['accion2_url'] = reverse_lazy('users:lista_personal')
        context['entity'] = 'ACTUALIZAR DATOS'
        context['entity_url'] = reverse_lazy('users:lista_personal') 
        return context 

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        slug = self.kwargs.get('slug', None)
        revisor_p = self.model.objects.get(slug=slug)
        user_p = self.second_model.objects.get(id=revisor_p.user.pk)
        persona_p = self.third_model.objects.get(id=revisor_p.persona.pk)
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST, request.FILES, instance=user_p)
        form3 = self.third_form_class(request.POST, instance=persona_p)
        if form2.is_valid() and form3.is_valid():          
            form2.save()
            form3.save()
            return HttpResponseRedirect(reverse('users:lista_personal', args=[]))
        else:
            return self.render_to_response(self.get_context_data(form=form, form2=form2, form3=form3))