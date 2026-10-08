from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Categoria, Cupom, Favorito, LojaParceira, Oferta, Usuario, Voto

TEMPLATE_PAINEL = "plataforma/adm/painel_adm.html"


def ofertas_ativas_qs():
    """Ofertas em vigência no momento."""
    agora = timezone.now()
    return (
        Oferta.objects
        .filter(data_inicio__lte=agora, data_fim__gte=agora)
        .select_related("loja", "categoria", "cupom")
    )


# =========================================================
# PÁGINA INICIAL
# =========================================================

def home(request):
    agora = timezone.now()
    ativas = ofertas_ativas_qs()

    recentes = ativas.order_by("-criado_em")[:12]
    hot = ativas.order_by("-votos", "-clicks")[:6]
    ofertas_relampago = ativas.filter(is_relampago=True).order_by("data_fim")[:4]

    categorias = Categoria.objects.order_by("nome")[:12]

    cupons = (
        Cupom.objects
        .filter(ativo=True, data_validade__gte=agora)
        .select_related("loja")
        .order_by("data_validade")[:6]
    )

    return render(request, "plataforma/index.html", {
        "offers": recentes,
        "hot": hot,
        "categorias": categorias,
        "coupons": cupons,
        "ofertas_relampago": ofertas_relampago,
    })


# =========================================================
# LISTAGEM PÚBLICA DE OFERTAS
# =========================================================

def ofertas(request):
    lista = ofertas_ativas_qs().order_by("data_fim")
    return render(request, "plataforma/ofertas.html", {"ofertas": lista})


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
        "total_destaques": Oferta.objects.filter(is_destaque=True).count(),
        "total_relampago": Oferta.objects.filter(is_relampago=True).count(),
        "total_com_cupom": Oferta.objects.filter(cupom__isnull=False).count(),
        "total_votos": Voto.objects.count(),
        "total_favoritos": Favorito.objects.count(),
        "total_clicks": Oferta.objects.aggregate(total=Sum("clicks"))["total"] or 0,
        "ofertas": (
            Oferta.objects
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
    lista = (
        Oferta.objects
        .select_related("loja", "categoria", "cupom")
        .order_by("-criado_em")
    )
    return render(request, TEMPLATE_PAINEL, {"ofertas": lista})


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


# =========================================================
# CRUD DE OFERTAS
# =========================================================

@staff_member_required
@require_POST
def excluir_oferta(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk)
    nome = oferta.nome_produto
    oferta.delete()

    messages.success(request, f'Oferta "{nome}" excluída com sucesso!')
    return redirect("adm_ofertas")

def login(request):
    return render(request, "plataforma/login/login.html")
