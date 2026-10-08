from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import *
from .forms import *


# =========================================================
# HOME
# =========================================================

def home(request):
    hoje = date.today()

    ofertas = (
        Oferta.objects
        .filter(data_fim__gte=hoje)
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-criado_em")[:12]
    )

    hot = (
        Oferta.objects
        .filter(data_fim__gte=hoje)
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-votos", "-clicks")[:6]
    )

    categorias = (
        Categoria.objects
        .all()
        .order_by("nome")[:12]
    )

    cupons = (
        Cupom.objects
        .filter(
            ativo=True,
            data_validade__gte=hoje,
        )
        .select_related("loja")
        .order_by("data_validade")[:6]
    )

    return render(
        request,
        "plataforma/index.html",
        {
            "offers": ofertas,
            "hot": hot,
            "categories": categorias,
            "coupons": cupons,
        },
    )

# =========================================================
# LOGIN
# =========================================================

def login(request):
    return render(
        request, 
        "plataforma/login/login.html"
    )

# =========================================================
# OFERTAS
# =========================================================

def offers(request):
    """
    Lista todas as ofertas válidas.
    Permite pesquisa, filtro por categoria
    e ordenação.
    """

    hoje = date.today()

    qs = (
        Oferta.objects
        .filter(data_fim__gte=hoje)
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
    )

    sort = request.GET.get("sort", "recent")
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()

    # Pesquisa
    if q:
        qs = qs.filter(
            Q(nome_produto__icontains=q)
            | Q(descricao__icontains=q)
            | Q(loja__nome__icontains=q)
            | Q(categoria__nome__icontains=q)
        )

    # Filtro por categoria
    if cat:
        try:
            qs = qs.filter(categoria_id=int(cat))
        except (ValueError, TypeError):
            pass

    # Ordenação
    if sort == "price":

        qs = qs.order_by("preco_atual")

    elif sort == "popular":

        qs = qs.order_by(
            "-votos",
            "-clicks",
        )

    elif sort == "discount":

        qs = sorted(
            qs,
            key=lambda oferta: oferta.desconto_percentual(),
            reverse=True,
        )

    else:

        qs = qs.order_by("-criado_em")

    return render(
        request,
        "offers/offers.html",
        {
            "offers": qs,
            "query": q,
            "sort": sort,
            "selected_category": cat,
        },
    )


# =========================================================
# CATEGORIA
# =========================================================

def category(request, categoria_id):
    """
    Exibe as ofertas de uma determinada categoria.
    """

    hoje = date.today()

    categoria = get_object_or_404(
        Categoria,
        pk=categoria_id,
    )

    ofertas = (
        Oferta.objects
        .filter(
            categoria=categoria,
            data_fim__gte=hoje,
        )
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-criado_em")
    )

    return render(
        request,
        "offers/offers.html",
        {
            "offers": ofertas,
            "query": categoria.nome,
            "sort": "recent",
            "category": categoria,
        },
    )


# =========================================================
# LOJAS
# =========================================================

def stores(request):
    """
    Lista as lojas cadastradas.
    """

    lojas = (
        loja.objects
        .all()
        .order_by("nome")
    )

    return render(
        request,
        "offers/stores.html",
        {
            "stores": lojas,
        },
    )


# =========================================================
# CUPONS
# =========================================================

def coupons(request):
    """
    Lista os cupons ativos e válidos.
    """

    hoje = date.today()

    cupons = (
        Cupom.objects
        .filter(
            ativo=True,
            data_validade__gte=hoje,
        )
        .select_related("loja")
        .order_by("data_validade")
    )

    return render(
        request,
        "offers/coupons.html",
        {
            "coupons": cupons,
        },
    )


# =========================================================
# BUSCA
# =========================================================

def search(request):
    """
    Reutiliza a página de ofertas como página de busca.
    """

    return offers(request)


# =========================================================
# DETALHES DA OFERTA
# =========================================================

def offer_detail(request, slug):
    """
    Exibe os detalhes de uma oferta.
    """

    hoje = date.today()

    oferta = get_object_or_404(
        Oferta.objects.select_related(
            "loja",
            "categoria",
            "cupom",
        ),
        slug=slug,
        data_fim__gte=hoje,
    )

    relacionadas = (
        Oferta.objects
        .filter(
            categoria=oferta.categoria,
            data_fim__gte=hoje,
        )
        .exclude(pk=oferta.pk)
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-criado_em")[:4]
    )

    is_favorite = False

    if request.user.is_authenticated:

        is_favorite = favorito.objects.filter(
            usuario=request.user,
            oferta=oferta,
        ).exists()

    return render(
        request,
        "offers/detail.html",
        {
            "offer": oferta,
            "related": relacionadas,
            "is_favorite": is_favorite,
        },
    )


# =========================================================
# FAVORITOS
# =========================================================

@login_required
def toggle_favorite(request, pk):
    """
    Adiciona ou remove uma oferta dos favoritos.
    """

    oferta = get_object_or_404(
        Oferta,
        pk=pk,
    )

    favorito_obj, created = favorito.objects.get_or_create(
        usuario=request.user,
        oferta=oferta,
    )

    if created:

        messages.success(
            request,
            "Oferta salva nos favoritos!",
        )

    else:

        favorito_obj.delete()

        messages.info(
            request,
            "Oferta removida dos favoritos.",
        )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "home",
        )
    )


# =========================================================
# VOTO
# =========================================================

@login_required
def vote(request, pk, value):
    """
    Registra um voto na oferta.

    value > 0 = positivo
    value <= 0 = negativo
    """

    oferta = get_object_or_404(
        Oferta,
        pk=pk,
    )

    try:
        value = int(value)
    except (ValueError, TypeError):
        value = 1

    valor_voto = 1 if value > 0 else -1

    voto_obj, created = voto.objects.get_or_create(
        usuario=request.user,
        oferta=oferta,
    )

    if created:

        oferta.votos += valor_voto

        oferta.save(
            update_fields=["votos"]
        )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "home",
        )
    )


# =========================================================
# CARRINHO
# =========================================================

def add_cart(request, pk):
    """
    Adiciona uma oferta ao carrinho da sessão.
    """

    oferta = get_object_or_404(
        Oferta,
        pk=pk,
    )

    cart = request.session.get(
        "cart",
        {},
    )

    produto_id = str(oferta.pk)

    cart[produto_id] = (
        cart.get(produto_id, 0) + 1
    )

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(
        request,
        "Oferta adicionada ao carrinho.",
    )

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "cart",
        )
    )


def remove_cart(request, pk):
    """
    Remove uma oferta do carrinho.
    """

    cart = request.session.get(
        "cart",
        {},
    )

    cart.pop(
        str(pk),
        None,
    )

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def cart(request):
    """
    Exibe o carrinho.
    """

    cart_data = request.session.get(
        "cart",
        {},
    )

    ids = []

    for item_id in cart_data.keys():

        try:
            ids.append(int(item_id))
        except (ValueError, TypeError):
            continue

    items = (
        Oferta.objects
        .filter(pk__in=ids)
        .select_related("loja")
    )

    total = sum(
        oferta.preco_atual
        * cart_data.get(str(oferta.pk), 0)
        for oferta in items
    )

    return render(
        request,
        "offers/cart.html",
        {
            "items": items,
            "cart": cart_data,
            "total": total,
        },
    )


# =========================================================
# CHECKOUT
# =========================================================

def checkout(request):
    """
    Checkout demonstrativo.

    Não existe model de pedido atualmente,
    portanto nenhuma compra é salva no banco.
    """

    cart_data = request.session.get(
        "cart",
        {},
    )

    if not cart_data:

        return redirect("cart")

    if request.method == "POST":

        request.session["cart"] = {}
        request.session.modified = True

        messages.success(
            request,
            "Pedido de demonstração recebido! "
            "Nenhuma cobrança real foi feita.",
        )

        return redirect("account")

    return render(
        request,
        "offers/checkout.html",
    )


# =========================================================
# CONTA DO USUÁRIO
# =========================================================

@login_required
def account(request):
    """
    Área do usuário.
    """

    favoritos = (
        favorito.objects
        .filter(usuario=request.user)
        .select_related(
            "oferta",
            "oferta__loja",
            "oferta__categoria",
        )
        .order_by("-criado_em")
    )

    votos = (
        voto.objects
        .filter(usuario=request.user)
        .select_related("oferta")
        .order_by("-criado_em")
    )

    return render(
        request,
        "offers/account.html",
        {
            "favorites": favoritos,
            "votes": votos,
        },
    )


# =========================================================
# CADASTRO
# =========================================================

def signup(request):
    """
    Cadastro de novos usuários.
    """

    if request.method == "POST":

        form = UserCreationForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            login(
                request,
                user,
            )

            messages.success(
                request,
                "Conta criada com sucesso!",
            )

            return redirect("account")

    else:

        form = UserCreationForm()

    return render(
        request,
        "registration/signup.html",
        {
            "form": form,
        },
    )


# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

@login_required
def admin_dashboard(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    hoje = date.today()

    # =========================
    # CONTADORES
    # =========================

    total_usuarios = Usuario.objects.count()

    total_ofertas = Oferta.objects.count()

    total_lojas = loja.objects.count()

    total_categorias = Categoria.objects.count()

    total_cupons_ativos = Cupom.objects.filter(
        ativo=True,
        data_validade__gte=hoje
    ).count()

    total_promocoes = Promocao.objects.count()

    total_destaques = Promocao.objects.filter(
        is_destaque=True
    ).count()

    total_relampago = Promocao.objects.filter(
        is_relampago=True
    ).count()

    total_com_cupom = Promocao.objects.filter(
        cupom__isnull=False
    ).count()

    total_votos = voto.objects.count()

    total_favoritos = favorito.objects.count()

    # =========================
    # TOTAL DE CLIQUES
    # =========================

    total_clicks = sum(
        Oferta.objects.values_list(
            "clicks",
            flat=True
        )
    )

    # =========================
    # PROMOÇÕES
    # =========================

    promocoes = (
        Promocao.objects
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-data_inicio")
    )

    # =========================
    # OFERTAS RECENTES
    # =========================

    ofertas_recentes = (
        Oferta.objects
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-criado_em")[:10]
    )

    # =========================
    # RENDER
    # =========================

    return render(
        request,
        "plataforma/adm/painel_adm.html",
        {
            "total_usuarios": total_usuarios,
            "total_ofertas": total_ofertas,
            "total_lojas": total_lojas,
            "total_categorias": total_categorias,
            "total_cupons_ativos": total_cupons_ativos,

            "total_promocoes": total_promocoes,
            "total_destaques": total_destaques,
            "total_relampago": total_relampago,
            "total_com_cupom": total_com_cupom,

            "total_votos": total_votos,
            "total_favoritos": total_favoritos,
            "total_clicks": total_clicks,

            "promocoes": promocoes,
            "ofertas_recentes": ofertas_recentes,
        }
    )

@login_required
def adm_usuarios(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    usuarios = Usuario.objects.all().order_by("-date_joined")

    return render(
        request,
        "plataforma/adm/painel_adm.html",
        {
            "usuarios": usuarios,
        }
    )


@login_required
def adm_ofertas(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    ofertas = (
        Oferta.objects
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-criado_em")
    )

    return render(
        request,
        "plataforma/adm/painel_adm.html",
        {
            "ofertas": ofertas,
        }
    )


@login_required
def adm_lojas(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    lojas = loja.objects.all().order_by("nome")

    return render(
        request,
        "plataforma/adm/painel_adm.html",
        {
            "lojas": lojas,
        }
    )


@login_required
def adm_categorias(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    categorias = Categoria.objects.all().order_by("nome")

    return render(
        request,
        "plataforma/adm/painel_adm.html",
        {
            "categorias": categorias,
        }
    )


@login_required
def adm_cupons(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    cupons = (
        Cupom.objects
        .select_related("loja")
        .order_by("-data_validade")
    )

    return render(
        request,
        "plataforma/adm/painel_adm.html",
        {
            "cupons": cupons,
        }
    )
@login_required
def adm_promocoes(request):

    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    promocoes = (
        Promocao.objects
        .select_related(
            "loja",
            "categoria",
            "cupom",
        )
        .order_by("-data_inicio")
    )

    return render(
        request,
        "plataforma/adm/painel_adm.html",
        {
            "promocoes": promocoes,
        }
    )


# =========================================================
# CRUD DE PROMOÇÕES
# =========================================================

@login_required
def excluir_promocao(request, pk):
    if not request.user.is_staff:
        messages.error(
            request,
            "Você não tem permissão para acessar o painel administrativo."
        )
        return redirect("index")

    promocao = get_object_or_404(Promocao, pk=pk)

    if request.method == "POST":
        nome = promocao.nome_produto
        promocao.delete()

        messages.success(
            request,
            f'Promoção "{nome}" excluída com sucesso!'
        )

    return redirect("painel_adm")