from django.urls import path
from . import views

urlpatterns = [
    # Público
    path("", views.home, name="index"),
    path("promocoes/", views.promocoes, name="promocoes"),

    # Painel administrativo
    path("adm/", views.admin_dashboard, name="painel_adm"),
    path("adm/promocoes/", views.adm_promocoes, name="adm_promocoes"),
    path("adm/promocoes/<int:pk>/excluir/", views.excluir_promocao, name="excluir_promocao"),
]