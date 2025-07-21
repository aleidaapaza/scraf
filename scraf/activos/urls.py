from django.urls import path
from activos.views import ListaActivos, RegistroActivo, RegistroActivoResponsable, VerActivo, ActualizarActivoResponsable
app_name = 'activos'

urlpatterns = [
    path('listaActivos/', ListaActivos.as_view(), name='lista_activos'),
    path('registroActivo/', RegistroActivo.as_view(), name='registro_activos'),
    path('registroActivoResponsable/', RegistroActivoResponsable.as_view(), name='registro_activos_responsable'),
    path('VerActivoResponsable/<slug:slug>', VerActivo.as_view(), name='ver_activos_responsable'),
    path('ActualizacionActivoResponsable/<slug:slug>', ActualizarActivoResponsable.as_view(), name='actualizar_activos_responsable'),
    
]