from django.urls import path
from revision.views import ListaRevisiones, RegistroRevisiones
app_name = 'revision'
urlpatterns = [ 
    path('listaRevisiones/', ListaRevisiones.as_view(), name='lista_revisiones'),
    path('registroRevisiones/', RegistroRevisiones.as_view(), name='registro_revisiones'),
]