from django.urls import path
from . import views


urlpatterns = [

    # Página inicial
    path(
        "",
        views.home,
        name="index",
    ),

    # Painel administrativo
    path(
        "adm/",
        views.admin_dashboard,
        name="painel_adm",
    ),

    # Ofertas
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

    # Categorias
    path(
        "categoria/<int:categoria_id>/",
        views.category,
        name="category",
    ),

    # Lojas
    path(
        "lojas/",
        views.stores,
        name="stores",
    ),

    # Cupons
    path(
        "cupons/",
        views.coupons,
        name="coupons",
    ),

    # Favoritos
    path(
        "oferta/<int:pk>/favorito/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),

    # Votos
    path(
        "oferta/<int:pk>/voto/<int:value>/",
        views.vote,
        name="vote",
    ),

    # Carrinho
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

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    # Conta
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
# ADMINISTRAÇÃO
# =====================================================

path(
    "adm/",
    views.admin_dashboard,
    name="painel_adm",
),

path(
    "adm/usuarios/",
    views.adm_usuarios,
    name="adm_usuarios",
),

path(
    "adm/ofertas/",
    views.adm_ofertas,
    name="adm_ofertas",
),

path(
    "adm/lojas/",
    views.adm_lojas,
    name="adm_lojas",
),

path(
    "adm/categorias/",
    views.adm_categorias,
    name="adm_categorias",
),

path(
    "adm/cupons/",
    views.adm_cupons,
    name="adm_cupons",
),
# =====================================================
# ADMINISTRAÇÃO
# =====================================================

path(
    "adm/",
    views.admin_dashboard,
    name="painel_adm",
),

path(
    "adm/usuarios/",
    views.adm_usuarios,
    name="adm_usuarios",
),

path(
    "adm/ofertas/",
    views.adm_ofertas,
    name="adm_ofertas",
),

path(
    "adm/lojas/",
    views.adm_lojas,
    name="adm_lojas",
),

path(
    "adm/categorias/",
    views.adm_categorias,
    name="adm_categorias",
),

path(
    "adm/cupons/",
    views.adm_cupons,
    name="adm_cupons",
),
path(
    "adm/promocoes/",
    views.adm_promocoes,
    name="adm_promocoes",
),



]
