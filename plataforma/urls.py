from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Público
    path("", views.home, name="index"),
    path("ofertas/", views.ofertas, name="ofertas"),
    path("promocoes/", RedirectView.as_view(pattern_name="ofertas", permanent=True)),
    path("login/", views.login, name="login"),
    path("cadastro/", views.cadastro, name="cadastro"),


    # Painel administrativo
    path("adm/", views.admin_dashboard, name="painel_adm"),
    path("adm/usuarios/", views.usuarios_adm, name="usuarios_adm"),
    path("adm/ofertas/", views.ofertas_adm, name="ofertas_adm"),

    path("adm/ofertas/<int:pk>/excluir/", views.excluir_oferta, name="excluir_oferta"),
    path("adm/lojas/", views.lojas_adm, name="lojas_adm"),
    path("adm/categorias/", views.categorias_adm, name="categorias_adm"),
    path("adm/cupons/", views.cupons_adm, name="cupons_adm"),
]