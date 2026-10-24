from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CadastroForm
from .models import Categoria, Cupom, Favorito, LojaParceira, Oferta, UsuarioReal, Voto
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

TEMPLATE_PAINEL = "plataforma/adm/painel_adm.html"
TEMPLATE_INDEX = "plataforma/index.html"
TEMPLATE_LOGIN = "plataforma/login/login.html"
TEMPLATE_CADASTRO = "plataforma/login/cadastro.html"
TEMPLATE_CADASTRO_ETAPA2 = "plataforma/login/cadastroetapa2.html"


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
    recentes = ativas.filter(is_destaque=False, is_relampago=False).order_by("-criado_em")[:8] ### Adicionado apenas 8 campos de ofertas recentes
    ofertas_relampago = ativas.filter(is_relampago=True).order_by("data_fim")[:4]
    ofertas_destaque = ativas.filter(is_destaque=True, is_relampago=False).order_by("-criado_em")[:8]

    lojas_parceiras = (
        LojaParceira.objects.all().order_by("nome")
    )

    categorias = (
        Categoria.objects
        .annotate(
            total_ativas=Count(
                "ofertas",
                filter=Q(ofertas__data_inicio__lte=agora, ofertas__data_fim__gte=agora),
            )
        )
        .order_by("-total_ativas", "nome")[:12]
    )

    # cupons2 = (
    #     Cupom.objects
    #     .filter(ativo=True, data_validade__gte=agora)
    #     .select_related("loja")
    #     .order_by("data_validade")[:6]
    # )

    cupons = Cupom.objects.all()

    return render(request, TEMPLATE_INDEX, {
        "recentes": recentes,
        "categorias": categorias,
        "cupons": cupons,
        "ofertas_relampago": ofertas_relampago,
        "ofertas_destaque": ofertas_destaque,
        "lojas_parceiras": lojas_parceiras,
    })


# =========================================================
# PAINEL ADMINISTRATIVO
# =========================================================

@staff_member_required
def admin_dashboard(request):
    agora = timezone.now()

    contexto = {
        "total_usuarios": UsuarioReal.objects.count(),
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
    usuarios = UsuarioReal.objects.order_by("-date_joined")
    return render(request, TEMPLATE_PAINEL, {"usuarios": usuarios})


@staff_member_required
def ofertas_adm(request):
    lista = (
        Oferta.objects
        .select_related("loja", "categoria", "cupom")
        .order_by("-criado_em")
    )
    return render(request, "plataforma/adm/ofertas_adm.html", {"ofertas": lista})

def cadastrar_oferta(request):
    return render(request, "plataforma/adm/forms/form_oferta.html")

def editar_oferta(request, id):
    oferta = Oferta.objects.get(id=id)
    return render(request, "plataforma/adm/forms/form_oferta.html", {"oferta": oferta})




@staff_member_required
def lojas_adm(request):
    lojas = LojaParceira.objects.order_by("nome")
    return render(request, "plataforma/adm/lojas_adm.html", {"lojas": lojas})


@staff_member_required
def categorias_adm(request):
    categorias = Categoria.objects.order_by("nome")
    return render(request, "plataforma/adm/categorias_adm.html", {"categorias": categorias})


@staff_member_required
def cupons_adm(request):
    cupons = Cupom.objects.select_related("loja").order_by("-data_validade")
    return render(request, "plataforma/adm/cupons_adm.html", {"cupons": cupons})

# =========================================================
# CRUD DE OFERTAS
# =========================================================

def ofertas(request, tipo="todas"):
    lista = ofertas_ativas_qs().order_by("data_fim")
    categorias = Categoria.objects.all()

    categoria_atual = request.GET.get("categoria", "")

    if tipo == "relampago":
        lista = lista.filter(is_relampago=True)

    if categoria_atual:
        lista = lista.filter(categoria__id=categoria_atual)

    context = {
        "ofertas": lista,
        "categorias": categorias,
        "tipo_pagina": tipo,
        "categoria_atual": categoria_atual,
    }

    return render(request, "plataforma/ofertas.html", context)

@staff_member_required
@require_POST
def excluir_oferta(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk)
    nome = oferta.nome_produto
    oferta.delete()

    messages.success(request, f'Oferta "{nome}" excluída com sucesso!')
    return redirect("adm_ofertas")

# =========================================================
# LOGIN E CADASTRO
# =========================================================

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("index")
    else:
        form = AuthenticationForm()
    return render(request, TEMPLATE_LOGIN, {"form": form})

def cadastro_etapa1(request):
    if request.method == "POST":
        form = CadastroForm(request.POST)
        
        # Remove temporariamente a validação dos campos que ficaram na etapa 2
        form.errors.pop('sexo', None)
        form.errors.pop('password1', None)
        form.errors.pop('password2', None)

        # Se os campos da primeira etapa estiverem corretos, avança
        campos_etapa1 = ['username', 'email', 'telefone', 'data_nascimento']
        if not any(campo in form.errors for campo in campos_etapa1):
            # Guarda os dados digitados na sessão para usar depois
            request.session['cadastro'] = {
                campo: request.POST.get(campo) for campo in campos_etapa1
            }
            return redirect("cadastro_etapa2")
    else:
        # Se o usuário voltar da etapa 2, os dados continuam preenchidos
        dados_salvos = request.session.get('cadastro', None)
        form = CadastroForm(initial=dados_salvos)
        
    return render(request, TEMPLATE_CADASTRO, {"form": form})

def cadastro_etapa2(request):
    if request.method == "POST":
        # 1. Pega os dados que guardamos na sessão (etapa 1)
        dados_completos = request.session['cadastro'].copy()
        
        # 2. Junta com os dados enviados agora (sexo, senha1, senha2)
        dados_completos.update(request.POST.dict())

        # 3. Alimenta o formulário com TODOS os dados juntos
        form = CadastroForm(dados_completos)
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("login")
    else:
        form = CadastroForm()
    return render(request, TEMPLATE_CADASTRO_ETAPA2, {"form": form})

