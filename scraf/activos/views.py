from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView, TemplateView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect

from users.models import User
from activos.models import Activo, Activo_responsable, Activos_line
from activos.forms import R_Activo, R_Activo_responsable, A_Activo

# Create your views here.
class ListaActivos(LoginRequiredMixin, ListView):
    model = Activo_responsable
    template_name = 'lista/activo.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'LISTA DE ACTIVOS EN LA INSTITUCION'
        context['object_list'] = self.model.objects.all()
        usuario = self.request.user
        usuario_d = User.objects.get(username = usuario)
        if usuario_d.g_Activos:
            context['entity_registro'] = reverse_lazy('activos:registro_activos', args=[])
            context['entity_registro_nom'] = 'REGISTRAR NUEVO ACTIVO'
            context['entity_registro2'] = reverse_lazy('activos:registro_activos_responsable', args=[])
            context['entity_registro_nom2'] = 'REGISTRAR NUEVO ACTIVO CON RESPONSABLE'
        return context
    
class RegistroActivo(LoginRequiredMixin, CreateView):
    model = Activo
    template_name = 'RegistroActualizacion/activo.html'
    form_class = R_Activo
    success_url = reverse_lazy('activos:lista_activos')
    def get_context_data(self, **kwargs):
        context = super(RegistroActivo, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        context['titulo'] = 'REGISTRO DE SOLO INFORMACION ACTIVO'
        context['subtitulo_1'] = 'DATOS DEL ACTIVO'
        context['accion'] = 'GUARDAR'
        context['accion2'] = 'CANCELAR'
        context['accion2_url'] = reverse_lazy('activos:lista_activos')
        return context
    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        form = self.form_class(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data.get('codigo')
            form.save()
            activos = Activo.objects.get(codigo = codigo)
            Activo_responsable.objects.create(
                activo = activos,                
            )
            activos_responsable = Activo_responsable.objects.get(activo = activos)
            Activos_line.objects.create(
                slug = activos_responsable.slug,
                observacion = 'Se registro solo los datos del activo',
                creador = usuario,
            )
            return HttpResponseRedirect(reverse('activos:lista_activos', args=[]))
        else:
            return self.render_to_response(self.get_context_data(form=form))


class RegistroActivoResponsable(LoginRequiredMixin, CreateView):
    model = Activo_responsable
    second_model = Activo
    template_name = 'RegistroActualizacion/activo.html'
    form_class = R_Activo_responsable
    second_form_class = R_Activo
    success_url = reverse_lazy('activos:lista_activos')
    def get_context_data(self, **kwargs):
        context = super(RegistroActivoResponsable, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        if 'form2' not in context:
            context['form2'] = self.second_form_class(self.request.GET)
        context['titulo'] = 'REGISTRO INFORMACION ACTIVO Y RESPONSABLE DEL ACTIVO'
        context['subtitulo_1'] = 'DATOS DEL RESPONSABLE'
        context['subtitulo_2'] = 'DATOS DEL ACTIVO'
        context['accion'] = 'GUARDAR'
        context['accion2'] = 'CANCELAR'
        context['accion2_url'] = reverse_lazy('activos:lista_activos')
        context['activate'] = True
        return context
    def post(self, request, *args, **kwargs):
        usuario = self.request.user
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)
        if form.is_valid() and form2.is_valid():
            codigo = form2.cleaned_data.get('codigo')
            responsable = form.cleaned_data.get('responsable')
            piso_ubicacion = form.cleaned_data.get('piso_ubicacion')
            oficina_ubicacion = form.cleaned_data.get('oficina_ubicacion')
            form2.save()
            activos = Activo.objects.get(codigo = codigo)
            activo_responsable = form.save(commit=False)
            activo_responsable.activo = activos
            activo_responsable.save()
            activos_responsable = Activo_responsable.objects.get(activo = activos)
            Activos_line.objects.create(
                slug = activos_responsable.slug,
                responsable = responsable,
                piso_ubicacion = piso_ubicacion,
                oficina_ubicacion = oficina_ubicacion,
                observacion = 'Se registro los datos del activo y del responsable',
                creador = usuario,
            )
            return HttpResponseRedirect(reverse('activos:lista_activos', args=[]))
        else:
            return self.render_to_response(self.get_context_data(form=form, form2=form2))

class VerActivo(LoginRequiredMixin, TemplateView):
    template_name = 'Visualizar/activo.html'
    def get_context_data(self, **kwargs):
        context = super(VerActivo, self).get_context_data(**kwargs)
        slug = self.kwargs.get('slug', None)
        activo = Activo_responsable.objects.get(slug=slug)
        activo_line = Activos_line.objects.filter(slug=slug).order_by('-fecha_registro')
        context['titulo'] = 'INFORMACION DEL ACTIVO'
        context['activo'] = activo
        context['line'] = activo_line
        return context
    
class ActualizarActivoResponsable(LoginRequiredMixin, UpdateView):
    model = Activo_responsable
    second_model = Activo
    template_name = 'RegistroActualizacion/activo.html'
    form_class = R_Activo_responsable
    second_form_class = A_Activo
    success_url = reverse_lazy('activos:lista_activos')

    def get_object(self, queryset=None):
        return Activo_responsable.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activo_responsable = self.get_object()
        activo = activo_responsable.activo

        context['form'] = kwargs.get('form', self.form_class(instance=activo_responsable))
        context['form2'] = kwargs.get('form2', self.second_form_class(instance=activo))
        
        context['titulo'] = 'ACTUALIZACIÓN DE INFORMACIÓN DE ACTIVO Y RESPONSABLE'
        context['subtitulo_1'] = 'DATOS DEL RESPONSABLE, UBICACION Y ESTADO DEL ACTIVO'
        context['subtitulo_2'] = 'DATOS DEL ACTIVO'
        context['accion'] = 'ACTUALIZAR'
        context['accion2'] = 'CANCELAR'
        context['accion2_url'] = reverse_lazy('activos:lista_activos')
        context['activate'] = True
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        usuario = self.request.user
        activo_responsable = self.object
        activo = activo_responsable.activo

        # Guardar valores originales
        old_responsable = activo_responsable.responsable
        old_piso = activo_responsable.piso_ubicacion
        old_oficina = activo_responsable.oficina_ubicacion
        old_estado = activo_responsable.estado

        form = self.form_class(request.POST, instance=activo_responsable)
        form2 = self.second_form_class(request.POST, instance=activo)

        if form.is_valid() and form2.is_valid():
            form2.save()
            form.save()

            # Nuevos valores (ya están guardados en DB, así que podemos recargar si quieres seguridad extra)
            nuevo_responsable = activo_responsable.responsable
            nuevo_piso = activo_responsable.piso_ubicacion
            nuevo_oficina = activo_responsable.oficina_ubicacion
            nuevo_estado = activo_responsable.estado

            # Comparar cambios
            cambios = []
            if old_responsable != nuevo_responsable:
                cambios.append("responsable")
            if old_piso != nuevo_piso or old_oficina != nuevo_oficina:
                cambios.append("ubicación")
            if old_estado != nuevo_estado:
                cambios.append("estado")

            if cambios:
                observacion = "Se actualizó la información del " + ", ".join(cambios)
            else:
                observacion = "No se realizaron cambios relevantes"

            # Crear línea de historial
            Activos_line.objects.create(
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
            return self.render_to_response(self.get_context_data(form=form, form2=form2))