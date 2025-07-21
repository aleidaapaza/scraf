from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, ListView, TemplateView, DetailView, View
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from inicio.form import LoginForm

# Create your views here.
class Index(TemplateView):
    template_name = 'index.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, 'index.html')  # Renderiza la página principal
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