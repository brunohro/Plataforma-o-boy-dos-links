from django.urls import path
from . import views


urlpatterns = [

    # =====================================================
    # PÁGINA INICIAL
    # =====================================================

    path(
        "",
        views.home,
        name="index",
    ),


    # =====================================================
    # OFERTAS
    # =====================================================

    path(
        "ofertas/",
        views.offers,
        name="offers",
    ),

    path(
        "oferta/<slug:slug>/",
        views.offer_detail,
        name="offer_detail",
    ),

    path(
        "buscar/",
        views.search,
        name="search",
    ),


    # =====================================================
    # CATEGORIAS
    # =====================================================

    path(
        "categoria/<int:categoria_id>/",
        views.categoria,
        name="categoria",
    ),


    # =====================================================
    # LOJAS
    # =====================================================

    path(
        "lojas/",
        views.stores,
        name="stores",
    ),


    # =====================================================
    # CUPONS
    # =====================================================

    path(
        "cupons/",
        views.coupons,
        name="coupons",
    ),


    # =====================================================
    # FAVORITOS
    # =====================================================

    path(
        "oferta/<int:pk>/favorito/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),


    # =====================================================
    # VOTOS
    # =====================================================

    path(
        "oferta/<int:pk>/voto/<int:value>/",
        views.vote,
        name="vote",
    ),


    # =====================================================
    # CARRINHO
    # =====================================================

    path(
        "carrinho/",
        views.cart,
        name="cart",
    ),

    path(
        "carrinho/adicionar/<int:pk>/",
        views.add_cart,
        name="add_cart",
    ),

    path(
        "carrinho/remover/<int:pk>/",
        views.remove_cart,
        name="remove_cart",
    ),


    # =====================================================
    # CHECKOUT
    # =====================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),


    # =====================================================
    # CONTA
    # =====================================================

    path(
        "conta/",
        views.account,
        name="account",
    ),

    path(
        "cadastro/",
        views.signup,
        name="signup",
    ),


    # =====================================================
    # PAINEL ADMINISTRATIVO
    # =====================================================

    # Página principal do ADM
    path(
        "adm/",
        views.admin_dashboard,
        name="painel_adm",
    ),

    # Usuários
    path(
        "adm/usuarios/",
        views.adm_usuarios,
        name="adm_usuarios",
    ),

    # Ofertas
    path(
        "adm/ofertas/",
        views.adm_ofertas,
        name="adm_ofertas",
    ),

    # Lojas
    path(
        "adm/lojas/",
        views.adm_lojas,
        name="adm_lojas",
    ),

    # Categorias
    path(
        "adm/categorias/",
        views.adm_categorias,
        name="adm_categorias",
    ),

    # Cupons
    path(
        "adm/cupons/",
        views.adm_cupons,
        name="adm_cupons",
    ),

    # =====================================================
    # PROMOÇÕES
    # =====================================================

    # Lista de promoções
    path(
        "adm/promocoes/",
        views.adm_promocoes,
        name="adm_promocoes",
    ),

    # Excluir promoção
    path(
        "adm/promocoes/<int:pk>/excluir/",
        views.excluir_promocao,
        name="excluir_promocao",
    ),
]