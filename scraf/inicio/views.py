from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, ListView, TemplateView, DetailView, View
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from activos.models import Activo_responsable

from inicio.form import LoginForm

# Create your views here.
class Index(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Solo los activos designados al usuario autenticado
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
        message = ''
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio:Index')  # Redirige al GET de esta misma vista
            else:
                message = 'Error al iniciar sesión. Verifica tu usuario y contraseña.'

        return render(request, 'homepage/login.html', {'form': form, 'message': message})

def cierreSesion(request):
    logout(request)
    messages.success(request, 'SESIÓN FINALIZADA EXITOSAMENTE')
    return redirect('inicio:Index')