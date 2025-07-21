from django.urls import path
from inicio.views import Index, cierreSesion
app_name = 'inicio'
urlpatterns = [
    path('', Index.as_view(), name='Index'),
    path('logout/', cierreSesion, name="Logout"),
]