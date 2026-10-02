from django.urls import path, include
from .views import index, painel_adm
urlpatterns = [
    path('', index, name='index'),
    path('adm/', painel_adm, name='painel_adm'),
]