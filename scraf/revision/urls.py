from django.urls import path
from revision.views import ListaRevisiones, ajax_r_Revision, ajax_editar_revision
app_name = 'revision'
urlpatterns = [ 
    path('listaRevisiones/', ListaRevisiones.as_view(), name='lista_revisiones'),
    path('ajax/R_revision/', ajax_r_Revision, name='ajax_r_Revision'),
    path('ajax/A_revision/<slug:slug>/', ajax_editar_revision, name='ajax_a_Revision'),
]