from django.urls import path

from designacion.views import ListaAsignaciones, crear_asignacion, crear_devolucion, get_activos_asignacion,confirmar_ubicacion, verAsignaciones, verDevolucion

app_name = 'designacion'
urlpatterns = [
    path('listaActivos/', ListaAsignaciones.as_view(), name='lista_asignaciones'),
    path('RegistroAsign/', crear_asignacion, name='registrar_asig'),
    path('DevolverAsign/', crear_devolucion, name='devolver_asig'),
    path('DevolverAsign/get-activos/', get_activos_asignacion, name='devolver_asig_get'),
    path('ConfirmacionUbicacion/<str:tipo>/<str:slug>/', confirmar_ubicacion, name='confirmacionUbicacion'),
    path('verAsignacion/<slug:slug>', verAsignaciones.as_view(), name='ver_asignaciones'),
    path('verDevolucion/<slug:slug>', verDevolucion.as_view(), name='ver_devolucion'),

]