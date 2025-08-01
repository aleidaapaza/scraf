from django.urls import path
from revision.views import (ListaRevisiones, ListaCambiosRevision, Revision_RActivos,
                            ajax_r_Revision, ajax_editar_revision, inicio_fin_Revision,ajax_ver_revision,
                            buscar_activo, actualizar_activo)
app_name = 'revision'
urlpatterns = [ 
    path('listaRevisiones/<slug:slug>/', ListaCambiosRevision.as_view(), name='lista_revisiones_line'),
    path('listaRevisiones/', ListaRevisiones.as_view(), name='lista_revisiones'),
    path('RevisionActivo/<slug:slug>/', Revision_RActivos.as_view(), name='revision_activo'),
    path('ajax/R_revision/', ajax_r_Revision, name='ajax_r_Revision'),
    path('ajax/A_revision/<slug:slug>/', ajax_editar_revision, name='ajax_a_Revision'),
    path('inicio-fin/<slug:slug>/', inicio_fin_Revision, name='inicio_fin_revision'),
    path('ajax/Ver_revision/<slug:slug>/', ajax_ver_revision, name='ajax_ver_Revision'),
    path('buscar_activo/<slug:slug>/', buscar_activo, name='buscar_activo'),
    path('actualizar_ver_activo/<slug:slug>/<str:codigo>/', actualizar_activo, name='vactualizar_activo'),
]