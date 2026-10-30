from django.urls import path
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Público
    path("", views.home, name="index"),
    path("login/", views.login_view, name="login"),
    path("cadastro/", views.cadastro_etapa1, name="cadastro"),
    path('cadastro/etapa2/', views.cadastro_etapa2, name='cadastro_etapa2'),

    # Cliques, votos e favoritos
    path("ir/<int:pk>/", views.ir_para_oferta, name="ir_para_oferta"),
    path("ofertas/<int:pk>/votar/", views.votar_oferta, name="votar_oferta"),
    path("ofertas/<int:pk>/favoritar/", views.favoritar_oferta, name="favoritar_oferta"),
    path("cupons/<int:pk>/copiar/", views.registrar_copia_cupom, name="registrar_copia_cupom"),
    path("cupons/<int:pk>/favoritar/", views.favoritar_cupom, name="favoritar_cupom"),
    path("favoritos/", views.favoritos, name="favoritos"),

    #ofertas e cupons
    path("ofertas/", views.ofertas, name="ofertas"),
    path("cupons/", views.cupons, name="cupons"),

    # Painel administrativo
    path("adm/", views.admin_dashboard, name="painel_adm"),
    path("adm/usuarios/", views.adm_usuarios, name="usuarios_adm"),
    path("adm/usuarios/<int:id>/permissao/", views.alterar_permissao_usuario, name="alterar_permissao_usuario"),

    # ofertas adm
    path("adm/ofertas/", views.ofertas_adm, name="ofertas_adm"),
    path("adm/ofertas/cadastrar", views.criar_oferta, name="cadastrar_oferta"),
    path("adm/ofertas/editar/<int:id>", views.editar_oferta, name="editar_oferta"),
    path("adm/ofertas/<int:id>/excluir/", views.excluir_oferta, name="excluir_oferta"),

    # cupons adm
    path("adm/cupons/", views.cupons_adm, name="cupons_adm"),
    path("adm/cupons/cadastrar", views.criar_cupom, name="cadastrar_cupom"),
    path("adm/cupons/editar/<int:id>", views.editar_cupom, name="editar_cupom"),
    path("adm/cupons/<int:id>/excluir/", views.excluir_cupom, name="excluir_cupom"),

    #categorias adm
    path("adm/categorias/", views.categorias_adm, name="categorias_adm"),
    path("adm/categorias/cadastrar", views.criar_categoria, name="cadastrar_categoria"),
    path("adm/categorias/editar/<int:id>", views.editar_categoria, name="editar_categoria"),
    path("adm/categorias/<int:id>/excluir/", views.excluir_categoria, name="excluir_categoria"),
    
    # lojas adm
    path("adm/lojas/", views.lojas_adm, name="lojas_adm"),
    path("adm/lojas/cadastrar/", views.cadastrar_loja, name="cadastrar_loja"),
    path("adm/lojas/editar/<int:id>/", views.editar_loja, name="editar_loja"),
    path("adm/lojas/<int:id>/excluir/", views.excluir_loja, name="excluir_loja"),


    path("ofertas/relampago/",views.ofertas,{"tipo": "relampago"}, name="ofertas_relampago",),
    path("promocoes/", RedirectView.as_view(pattern_name="ofertas", permanent=True)),

    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )