from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from designacion.models import Activo_responsable

from inicio.form import LoginForm
from django.shortcuts import render
from django.views.generic import TemplateView
from revision.views import get_menu_context
from activos.models import Activo
from django.contrib import messages

class Index(TemplateView): 
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        context.update(get_menu_context(self.request))
        if self.request.user.is_authenticated:
            context['activos_total'] = Activo.objects.all().count()
            context['activos_asignados'] = Activo.objects.filter(estadoDesignacion=True).count()
            context['activos_sin_asignar'] = Activo.objects.filter(estadoDesignacion=False).count()
            context['activos_mantenimiento'] = Activo.objects.filter(mantenimiento=True).count()

            context['object_list'] = Activo_responsable.objects.filter(responsable__user=self.request.user)
        return context
    
    def get(self, request):
        if request.user.is_authenticated:

            return render(request, 'index.html', self.get_context_data())
        else:
            form = LoginForm()
            entity = 'Inicio de sesión'
            return render(request, 'homepage/login.html', {'form': form, 'entity': entity})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio:Index')
            else:
                messages.error(request, 'Error al iniciar sesión. Verifica tu usuario y contraseña.')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
        
        return render(request, 'homepage/login.html', {'form': form, 'entity': 'Inicio de sesión'})

def cierreSesion(request):
    logout(request)
    messages.success(request, 'SESIÓN FINALIZADA EXITOSAMENTE')
    return redirect('inicio:Index')