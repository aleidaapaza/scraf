from django.urls import path
from users.views import ListaPersonal, RegistroPersonal, ActualizacionPersonal, ListaCambiosPersonal

app_name = 'users'
urlpatterns = [
    path('listaPersonal/', ListaPersonal.as_view(), name='lista_personal'),
    path('RegistroPersonal/', RegistroPersonal.as_view(), name='registro_personal'),
    path('ActualizacionPersonal/<slug:slug>', ActualizacionPersonal.as_view(), name='actualizacion_personal'),
    path('linePersona/<slug:slug>', ListaCambiosPersonal.as_view(), name='line_personal'),
]