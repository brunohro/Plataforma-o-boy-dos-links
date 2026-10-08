from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import*

TEMPLATE_PAINEL = "plataforma/adm/painel_adm.html"


# =========================================================
# PÁGINA INICIAL
# =========================================================

def home(request):
    agora = timezone.now()

    ofertas_ativas = (
        Oferta.objects
        .filter(data_inicio__lte=agora, data_fim__gte=agora)
        .select_related("loja", "categoria", "cupom")
    )

    ofertas = ofertas_ativas.order_by("-criado_em")[:12]
    hot = ofertas_ativas.order_by("-votos", "-clicks")[:6]

    categorias = Categoria.objects.order_by("nome")[:12]

    cupons = (
        Cupom.objects
        .filter(ativo=True, data_validade__gte=agora)
        .select_related("loja")
        .order_by("data_validade")[:6]
    )

    promocoes_relampago = (
        Promocao.objects
        .filter(is_relampago=True, data_inicio__lte=agora, data_fim__gte=agora)
        .select_related("loja", "categoria", "cupom")
        .order_by("data_fim")[:4]
    )

    return render(request, "plataforma/index.html", {
        "offers": ofertas,
        "hot": hot,
        "categorias": categorias,
        "coupons": cupons,
        "promocoes_relampago": promocoes_relampago,
    })


# =========================================================
# LISTAGEM PÚBLICA DE PROMOÇÕES
# =========================================================

def promocoes(request):
    agora = timezone.now()

    lista = (
        Promocao.objects
        .filter(data_inicio__lte=agora, data_fim__gte=agora)
        .select_related("loja", "categoria", "cupom")
        .order_by("data_fim")
    )

    return render(request, "plataforma/promocoes.html", {"promocoes": lista})


# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

@staff_member_required
def admin_dashboard(request):
    agora = timezone.now()

    contexto = {
        "total_usuarios": Usuario.objects.count(),
        "total_ofertas": Oferta.objects.count(),
        "total_lojas": LojaParceira.objects.count(),
        "total_categorias": Categoria.objects.count(),
        "total_cupons_ativos": Cupom.objects.filter(
            ativo=True, data_validade__gte=agora
        ).count(),
        "total_promocoes": Promocao.objects.count(),
        "total_destaques": Promocao.objects.filter(is_destaque=True).count(),
        "total_relampago": Promocao.objects.filter(is_relampago=True).count(),
        "total_com_cupom": Promocao.objects.filter(cupom__isnull=False).count(),
        "total_votos": Voto.objects.count(),
        "total_favoritos": Favorito.objects.count(),
        "total_clicks": Oferta.objects.aggregate(total=Sum("clicks"))["total"] or 0,
        "promocoes": (
            Promocao.objects
            .select_related("loja", "categoria", "cupom")
            .order_by("-data_inicio")
        ),
        "ofertas_recentes": (
            Oferta.objects
            .select_related("loja", "categoria", "cupom")
            .order_by("-criado_em")[:10]
        ),
    }

    return render(request, TEMPLATE_PAINEL, contexto)


@staff_member_required
def adm_usuarios(request):
    usuarios = Usuario.objects.order_by("-date_joined")
    return render(request, TEMPLATE_PAINEL, {"usuarios": usuarios})


@staff_member_required
def adm_ofertas(request):
    ofertas = (
        Oferta.objects
        .select_related("loja", "categoria", "cupom")
        .order_by("-criado_em")
    )
    return render(request, TEMPLATE_PAINEL, {"ofertas": ofertas})


@staff_member_required
def adm_lojas(request):
    lojas = LojaParceira.objects.order_by("nome")
    return render(request, TEMPLATE_PAINEL, {"lojas": lojas})


@staff_member_required
def adm_categorias(request):
    categorias = Categoria.objects.order_by("nome")
    return render(request, TEMPLATE_PAINEL, {"categorias": categorias})


@staff_member_required
def adm_cupons(request):
    cupons = Cupom.objects.select_related("loja").order_by("-data_validade")
    return render(request, TEMPLATE_PAINEL, {"cupons": cupons})


@staff_member_required
def adm_promocoes(request):
    lista = (
        Promocao.objects
        .select_related("loja", "categoria", "cupom")
        .order_by("-data_inicio")
    )
    return render(request, TEMPLATE_PAINEL, {"promocoes": lista})


# =========================================================
# CRUD DE PROMOÇÕES
# =========================================================

@staff_member_required
@require_POST
def excluir_promocao(request, pk):
    promocao = get_object_or_404(Promocao, pk=pk)
    nome = promocao.nome_produto
    promocao.delete()

    messages.success(request, f'Promoção "{nome}" excluída com sucesso!')
    return redirect("adm_promocoes")