from django.urls import path

from designacion.views import ListaAsignaciones, crear_asignacion

app_name = 'designacion'
urlpatterns = [
    path('listaActivos/', ListaAsignaciones.as_view(), name='lista_asignaciones'),
    path('RegistroAsign/', crear_asignacion, name='registrar_asig'),

]