from django.urls import path
from users.views import ListaPersonal, RegistroPersonal, ActualizacionPersonal, ListaCambiosPersonal
from activos.views_b import CargaMasivaPersonalView

app_name = 'users'
urlpatterns = [
    path('listaPersonal/', ListaPersonal.as_view(), name='lista_personal'),
    path('RegistroPersonal/', RegistroPersonal.as_view(), name='registro_personal'),
    path('ActualizacionPersonal/<slug:slug>', ActualizacionPersonal.as_view(), name='actualizacion_personal'),
    path('linePersona/<slug:slug>', ListaCambiosPersonal.as_view(), name='line_personal'),
    path('CargaDatosPersonal/', CargaMasivaPersonalView.as_view(), name='carga_datos_personal'),

]