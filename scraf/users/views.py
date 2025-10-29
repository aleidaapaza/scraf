from django.forms import ValidationError
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, View, ListView, UpdateView
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect

from users.models import Personal, Persona, User, LinePersona
from users.forms import R_User, R_Persona, A_User, A_Personal

from revision.views import get_menu_context

def registrar_line_Persona(datos_antiguos_user, datos_antiguos_persona, slug, usuario):
    try:
        personal = Personal.objects.get(slug=slug)
        
        # Construir texto de permisos ANTIGUOS
        permisos_antiguos = []
        if datos_antiguos_user.get('is_encargado'):
            permisos_antiguos.append("Encargado")
        elif datos_antiguos_user.get('is_revisor'):
            permisos_antiguos.append("Apoyo Revisión")
            
        if datos_antiguos_user.get('g_Activos'):
            permisos_antiguos.append("Gestionar activos")
        elif datos_antiguos_user.get('v_Activos'):
            permisos_antiguos.append("Solo ver los activos")
            
        if datos_antiguos_user.get('g_personal'):
            permisos_antiguos.append("Gestión de Personal")
            
        if datos_antiguos_user.get('g_mantenimiento'):
            permisos_antiguos.append("Gestión de mantenimiento")
            
        if datos_antiguos_user.get('is_active'):
            permisos_antiguos.append("Usuario activo")
        else:
            permisos_antiguos.append("Usuario inactivo")

        # Construir texto de permisos NUEVOS (actuales)
        permisos_nuevos = []
        if personal.user.is_encargado: 
            permisos_nuevos.append("Encargado")
        elif personal.user.is_revisor:
            permisos_nuevos.append("Apoyo Revisión")
            
        if personal.user.g_Activos:
            permisos_nuevos.append("Gestionar activos")
        elif personal.user.v_Activos:
            permisos_nuevos.append("Solo ver los activos")
            
        if personal.user.g_personal:
            permisos_nuevos.append("Gestión de Personal")
            
        if personal.user.g_mantenimiento:
            permisos_nuevos.append("Gestión de mantenimiento")
            
        if personal.user.is_active:
            permisos_nuevos.append("Usuario activo")
        else:
            permisos_nuevos.append("Usuario inactivo")

        # Datos de persona
        cargo_antiguo = datos_antiguos_persona.get('cargo', 'No especificado')
        contacto_antiguo = datos_antiguos_persona.get('contacto', 'No especificado')
        
        cargo_nuevo = personal.persona.cargo if hasattr(personal.persona, 'cargo') else 'No especificado'
        contacto_nuevo = personal.persona.contacto if hasattr(personal.persona, 'contacto') else 'No especificado'

        # Verificar si es primera vez o actualización
        line_exists = LinePersona.objects.filter(persona=personal).exists()
        
        if not line_exists:
            # PRIMER REGISTRO
            text = f"""
            Se creó el usuario: {personal.user.username}
            
            PERMISOS INICIALES:
            {', '.join(permisos_nuevos) if permisos_nuevos else 'Sin permisos específicos'}
            
            DATOS PERSONALES:
            Cargo: {cargo_nuevo}
            Contacto: {contacto_nuevo}
            """
        else:
            # REGISTRO DE ACTUALIZACIÓN - Comparar cambios
            cambios = []
            
            # Comparar permisos de usuario
            if datos_antiguos_user.get('is_encargado') != personal.user.is_encargado:
                cambios.append(f"Encargado: {datos_antiguos_user.get('is_encargado')} → {personal.user.is_encargado}")
            if datos_antiguos_user.get('is_revisor') != personal.user.is_revisor:
                cambios.append(f"Revisor: {datos_antiguos_user.get('is_revisor')} → {personal.user.is_revisor}")
            if datos_antiguos_user.get('g_personal') != personal.user.g_personal:
                cambios.append(f"Gestión Personal: {datos_antiguos_user.get('g_personal')} → {personal.user.g_personal}")
            if datos_antiguos_user.get('g_mantenimiento') != personal.user.g_mantenimiento:
                cambios.append(f"Gestión Mantenimiento: {datos_antiguos_user.get('g_mantenimiento')} → {personal.user.g_mantenimiento}")
            if datos_antiguos_user.get('g_Activos') != personal.user.g_Activos:
                cambios.append(f"Gestión Activos: {datos_antiguos_user.get('g_Activos')} → {personal.user.g_Activos}")
            if datos_antiguos_user.get('v_Activos') != personal.user.v_Activos:
                cambios.append(f"Ver Activos: {datos_antiguos_user.get('v_Activos')} → {personal.user.v_Activos}")
            if datos_antiguos_user.get('is_active') != personal.user.is_active:
                cambios.append(f"Activo: {datos_antiguos_user.get('is_active')} → {personal.user.is_active}")
                
            # Comparar datos de persona
            if cargo_antiguo != cargo_nuevo:
                cambios.append(f"Cargo: {cargo_antiguo} → {cargo_nuevo}")
            if contacto_antiguo != contacto_nuevo:
                cambios.append(f"Contacto: {contacto_antiguo} → {contacto_nuevo}")

            text = f"""
            Se actualizó el usuario: {personal.user.username}
            CAMBIOS REALIZADOS:
            {chr(10).join(f'- {cambio}' for cambio in cambios) if cambios else 'Sin cambios detectados'}
            
            ESTADO ANTERIOR:
            Permisos: {', '.join(permisos_antiguos) if permisos_antiguos else 'Ninguno'}
            Cargo: {cargo_antiguo}
            Contacto: {contacto_antiguo}
            
            ESTADO ACTUAL:
            Permisos: {', '.join(permisos_nuevos) if permisos_nuevos else 'Ninguno'}
            Cargo: {cargo_nuevo}
            Contacto: {contacto_nuevo}
            """

        # Crear el registro en LinePersona
        LinePersona.objects.create(
            persona=personal,
            encargado=usuario,
            observacion=text.strip(),
        )
        
        return f"Registro creado exitosamente para {personal.user.username}"
        
    except Personal.DoesNotExist:
        return f"Error: No se encontró Personal con slug {slug}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"
        
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
        context.update(get_menu_context(self.request))
        return context
    
class RegistroPersonal(LoginRequiredMixin, CreateView):
    model = Personal
    template_name = 'RegistroActualizacion/personal.html'
    form_class = R_Persona
    second_form_class = R_User
    success_url = reverse_lazy('users:lista_personal')

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
        context['accion2_url'] = reverse_lazy('users:lista_personal')
        context['activate'] = True
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)

        if form.is_valid() and form2.is_valid():
            datos_antiguos_user = {
                    'is_encargado': "",
                    'is_revisor': "",
                    'g_personal': "",
                    'g_mantenimiento': "",
                    'g_Activos': "",
                    'v_Activos': "",
                    'is_active': ""
                }
            datos_antiguos_persona ={
                    'cargo':"",
                    'contacto':""
                }
            carnet = form.cleaned_data.get('carnet')
            usuario = form2.save(commit=False)
            usuario.is_personal = True
            usuario.is_active  = True
            usuario.password = f'{carnet}'
            usuario.set_password(usuario.password)
            
            rol_rev = request.POST.get('rol_revision', '')
            usuario.is_encargado = (rol_rev == 'encargado')
            usuario.is_revisor = (rol_rev == 'apoyo')

            rol_independientes = request.POST.get('rol_independientes', '')
            roles_independientes = rol_independientes.split(',') if rol_independientes else []

            usuario.g_personal = 'personal' in roles_independientes
            usuario.g_mantenimiento = 'mantenimiento' in roles_independientes

            rol_activos_exclusivo = request.POST.get('rol_activos_exclusivo', '')
            usuario.g_Activos = (rol_activos_exclusivo == 'gestion_activos')
            usuario.v_Activos = (rol_activos_exclusivo == 'solo_visualiza')        
            usuario.save()
            persona = form.save()
            personal = Personal.objects.create(persona=persona, user=usuario)
            line = registrar_line_Persona(
                    datos_antiguos_user, 
                    datos_antiguos_persona, 
                    personal.slug, 
                    request.user  # El usuario que está haciendo la modificación
                )
            print(line)
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
        context['personal'] = personal_p
        context['titulo'] = 'ACTUALIZAR DATOS DEL PERSONAL'
        context['accion2'] = 'Cancelar'
        context['accion2_url'] = reverse_lazy('users:lista_personal')
        context['entity'] = 'ACTUALIZAR DATOS'
        context['entity_url'] = reverse_lazy('users:lista_personal') 
        return context
   
   def post(self, request, *args, **kwargs):
            self.object = self.get_object()
            slug = self.kwargs.get('slug', None)
            usuario = self.request.user
            revisor_p = self.model.objects.get(slug=slug)
            user_p = self.second_model.objects.get(id=revisor_p.user.pk)
            persona_p = self.third_model.objects.get(id=revisor_p.persona.pk)
            form = self.form_class(request.POST)
            form2 = self.second_form_class(request.POST, request.FILES, instance=user_p)
            form3 = self.third_form_class(request.POST, instance=persona_p)
            if form2.is_valid() and form3.is_valid():
                datos_antiguos_user = {
                    'is_encargado': user_p.is_encargado,
                    'is_revisor': user_p.is_revisor,
                    'g_personal': user_p.g_personal,
                    'g_mantenimiento': user_p.g_mantenimiento,
                    'g_Activos': user_p.g_Activos,
                    'v_Activos': user_p.v_Activos,
                    'is_active': user_p.is_active
                }
                datos_antiguos_persona ={
                    'cargo':persona_p.cargo,
                    'contacto':persona_p.contacto
                }
                usuario = form2.save(commit=False)
                rol_rev = request.POST.get('rol_revision', '')
                usuario.is_encargado = (rol_rev == 'encargado')
                usuario.is_revisor = (rol_rev == 'apoyo')

                # Grupo B: Independientes (múltiples valores)
                rol_independientes = request.POST.get('rol_independientes', '')
                #print(rol_independientes)
                roles_independientes = rol_independientes.split(',') if rol_independientes else []

                usuario.g_personal = 'personal' in roles_independientes
                usuario.g_mantenimiento = 'mantenimiento' in roles_independientes
                usuario.is_active = 'Useractivo' in roles_independientes

                # Grupo C: Activos (exclusivo - solo uno)
                rol_activos_exclusivo = request.POST.get('rol_activos_exclusivo', '')
                usuario.g_Activos = (rol_activos_exclusivo == 'gestion_activos')
                usuario.v_Activos = (rol_activos_exclusivo == 'solo_visualiza')        
                usuario.save()
                form3.save()
                line = registrar_line_Persona(
                    datos_antiguos_user, 
                    datos_antiguos_persona, 
                    slug, 
                    request.user  # El usuario que está haciendo la modificación
                )
                print(line)          
                return HttpResponseRedirect(reverse('users:lista_personal', args=[]))
            else:
                return self.render_to_response(self.get_context_data(form=form, form2=form2, form3=form3))

class ListaCambiosPersonal(LoginRequiredMixin, ListView):
    model = LinePersona
    template_name = "lista/personal_line.html"

    def get_context_data(self, **kwargs):
        context = super(ListaCambiosPersonal, self).get_context_data(**kwargs)
        slug = self.kwargs.get("slug", None)
        context["titulo"] = "LISTA DE CAMBIOS DE DATOS DEL PERSONAL"
        context["object_list"] = self.model.objects.filter(
            persona__slug = slug 
        ).order_by("-fechaRegistro")
        return context

