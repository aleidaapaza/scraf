from django.urls import path
from activos.views import ListaActivos, RegistroActivo, RegistroActivoResponsable, VerActivo, ActualizarActivoResponsable,ajax_r_activo, ajax_r_activo_responsable
from activos.views_b import ListaGruposContables, CargaContableView, ListaAuxiliatesContables, verAuxiliares
app_name = 'activos'

urlpatterns = [
    path('listaActivos/', ListaActivos.as_view(), name='lista_activos'),
    path('registroActivo/', RegistroActivo.as_view(), name='registro_activos'),
    path('registroActivoResponsable/', RegistroActivoResponsable.as_view(), name='registro_activos_responsable'),
    path('VerActivoResponsable/<slug:slug>', VerActivo.as_view(), name='ver_activos_responsable'),
    path('ActualizacionActivoResponsable/<slug:slug>', ActualizarActivoResponsable.as_view(), name='actualizar_activos_responsable'),
    path('verActivo/<slug:slug>/', VerActivo.as_view(), name='ver_activo'),
    path('ajax/registro/', ajax_r_activo, name='ajax_r_activo'),
    path('ajax/registro_con_responsable/', ajax_r_activo_responsable, name='ajax_r_activo_resp'),
    #Grupos Contables y Auxiliares
    path('listaGrupoContable/', ListaGruposContables.as_view(), name='lista_GrupoContable'),
    path('listaAuxiliaresContable/', ListaAuxiliatesContables.as_view(), name='lista_AuxiliaresContable'),
    path('CargarInf/', CargaContableView.as_view(), name='cargarInformacion'),
    path('verGrupoAux/<int:pk>/', verAuxiliares.as_view(), name='ver_grupoAux'),

]