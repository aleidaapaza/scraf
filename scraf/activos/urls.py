from django.urls import path
from activos.views import (ListaActivos, RegistroActivo, RegistroActivoResponsable, VerActivo, ActualizarActivoResponsable, 
                                                ajax_r_activo, ajax_r_activo_responsable, get_auxiliares_por_grupo,
                                                LineActivo, gestionar_activo )
from activos.views_b import (ListaGruposContables, CargaContableView, ListaAuxiliatesContables, verAuxiliares, CargaDirectaActivosView,
                                                    )
app_name = 'activos'

urlpatterns = [
    #ListaActivos
    path('listaActivos/', ListaActivos.as_view(), name='lista_activos'),
    path('registroActivo/', RegistroActivo.as_view(), name='registro_activos'),

    path('registroActivoResponsable/', RegistroActivoResponsable.as_view(), name='registro_activos_responsable'),
    path('VerActivoResponsable/<slug:slug>', VerActivo.as_view(), name='ver_activos_responsable'),
    path('ActualizacionActivoResponsable/<slug:slug>', ActualizarActivoResponsable.as_view(), name='actualizar_activos_responsable'),
    path('ajax/registro/', ajax_r_activo, name='ajax_r_activo'),
    path('ajax/registro_con_responsable/', ajax_r_activo_responsable, name='ajax_r_activo_resp'),
    #Grupos Contables y Auxiliares
    path('listaGrupoContable/', ListaGruposContables.as_view(), name='lista_GrupoContable'),
    path('listaAuxiliaresContable/', ListaAuxiliatesContables.as_view(), name='lista_AuxiliaresContable'),
    path('CargarInf/', CargaContableView.as_view(), name='cargarInformacion'),
    path('verGrupoAux/<int:pk>/', verAuxiliares.as_view(), name='ver_grupoAux'),
    path('get-auxiliares/', get_auxiliares_por_grupo, name='Auxiliares_por_grupo'),
    path('listaLine/<slug:codigo>', LineActivo.as_view(), name='lista_lineactivo'),
    #actualizarDatos
    path('verActivo/<slug:codigo>/', VerActivo.as_view(), name='ver_activo'),
    path('gestionar-activo/<slug:activo_codigo>/', gestionar_activo, name='gestionar_activo'),
    #RegistomasivoActivos
    path('CargarActivos/', CargaDirectaActivosView.as_view(), name='cargaMasivaActivos'),
]