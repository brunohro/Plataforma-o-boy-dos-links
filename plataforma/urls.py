from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    # Público
    path("", views.home, name="index"),
    path("ofertas/", views.ofertas, name="ofertas"),
    # Mantém links antigos funcionando
    path("promocoes/", RedirectView.as_view(pattern_name="ofertas", permanent=True)),
    path("login/", views.login, name="login"),

    # Painel administrativo
    path("adm/", views.admin_dashboard, name="painel_adm"),
    path("adm/usuarios/", views.adm_usuarios, name="adm_usuarios"),
    path("adm/ofertas/", views.adm_ofertas, name="adm_ofertas"),
    path("adm/ofertas/<int:pk>/excluir/", views.excluir_oferta, name="excluir_oferta"),
    path("adm/lojas/", views.adm_lojas, name="adm_lojas"),
    path("adm/categorias/", views.adm_categorias, name="adm_categorias"),
    path("adm/cupons/", views.adm_cupons, name="adm_cupons"),
]