#########################################################
# IMPORTS
#########################################################

from django.contrib import messages
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from .forms import CadastroForm, OfertaForm, CategoriaForm, LojaParceiraForm, CupomForm
from .models import Banner, Categoria, Cupom, Favorito, LojaParceira, Oferta, UsuarioReal, Voto, ClickOferta, ClickCupom, FavoritoCupom
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.http import url_has_allowed_host_and_scheme


#########################################################
# CONSTANTES
#########################################################

TEMPLATE_PAINEL = "plataforma/adm/painel_adm.html"
TEMPLATE_INDEX = "plataforma/index.html"
TEMPLATE_LOGIN = "plataforma/login/login.html"
TEMPLATE_CADASTRO = "plataforma/login/cadastro.html"
TEMPLATE_CADASTRO_ETAPA2 = "plataforma/login/cadastroetapa2.html"


#########################################################
# FUNÇÕES AUXILIARES (QUERYSETS / INTERAÇÕES)
#########################################################

def cupons_ativos_qs():
    """Cupons em vigência no momento."""
    agora = timezone.now()
    return (
        Cupom.objects
        .filter(ativo=True, data_validade__gte=agora)
        .select_related("loja")
        .annotate(
            total_usos=Count("clicks_registros_cupons", distinct=True),
            total_favoritos=Count("favoritoscupons", distinct=True),
        )
    )


def ofertas_ativas_qs():
    """Ofertas em vigência no momento."""
    agora = timezone.now()
    return (
        Oferta.objects
        .filter(data_inicio__lte=agora, data_fim__gte=agora)
        .select_related("loja", "categoria", "cupom")
        .annotate(
            total_votos=Count("votos_registros", distinct=True),
            total_favoritos=Count("favoritos", distinct=True),
            total_clicks=Count("clicks_registros", distinct=True),
        )
    )


def interacoes(user):
    """Retorna as interações do usuário com as ofertas."""
    if user.is_authenticated:
        votos = Voto.objects.filter(usuario=user).values_list("oferta_id", flat=True)
        favoritos = Favorito.objects.filter(usuario=user).values_list("oferta_id", flat=True)
        favoritos_cupons = FavoritoCupom.objects.filter(usuario=user).values_list("cupom_id", flat=True)
        return {
            "votos": set(votos),
            "favoritos": set(favoritos),
            "favoritos_cupons_ids": set(favoritos_cupons),
        }
    return {"votos": set(), "favoritos": set(), "favoritos_cupons_ids": set()}


def ofertas_recomendadas(user):
    """Retorna ofertas recomendadas com base nas interações do usuário."""
    if user.is_authenticated:
        interacoes_usuario = interacoes(user)
        categorias_interagidas = (
            Oferta.objects
            .filter(id__in=interacoes_usuario["votos"] | interacoes_usuario["favoritos"])
            .values_list("categoria_id", flat=True)
        )
        return (
            ofertas_ativas_qs()
            .filter(categoria_id__in=categorias_interagidas)
            .exclude(id__in=interacoes_usuario["votos"] | interacoes_usuario["favoritos"])
            .order_by("-data_inicio")[:8]
        )
    return ofertas_ativas_qs().order_by("-data_inicio")[:8]


#########################################################
# PÁGINAS PÚBLICAS (USUÁRIO)
#########################################################


# MEU PERFIL 

def minha_conta(request, id):
    usuario = UsuarioReal.objects.get(id=id)
    return render(request, "plataforma/minha_conta.html", {"usuario": usuario})


# =========================================================
# PÁGINA INICIAL
# =========================================================

def home(request):
    agora = timezone.now()
    ativas = ofertas_ativas_qs()
    recentes = ativas.filter(is_relampago=False, is_destaque=False).order_by("-criado_em")[:8] ### Adicionado apenas 8 campos de ofertas recentes
    ofertas_relampago = ativas.filter(is_relampago=True).order_by("data_fim")[:4]
    ofertas_destaque = ativas.filter(is_destaque=True, is_relampago=False).order_by("-criado_em")[:8]
    mais_votadas = ativas.order_by("-total_votos")[:8]
    mais_favoritas = ativas.order_by("-total_favoritos")[:8]
    mais_acessadas = ativas.order_by("-total_clicks")[:8]
    recomendadas = ofertas_recomendadas(request.user)[:8]
    banners = Banner.objects.filter(ativo=True).order_by("ordem")

    lojas_parceiras = (
        LojaParceira.objects
        .annotate(
            total_cupons=Count(
                "cupons",
                filter=Q(cupons__ativo=True, cupons__data_validade__gte=agora),
            )
        )
        .order_by("nome")
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

    cupons = cupons_ativos_qs().order_by("data_validade")[:6]

    return render(request, TEMPLATE_INDEX, {
        "recentes": recentes,
        "categorias": categorias,
        "cupons": cupons,
        "ofertas_relampago": ofertas_relampago,
        "ofertas_destaque": ofertas_destaque,
        "lojas_parceiras": lojas_parceiras,
        "mais_votadas": mais_votadas,
        "mais_favoritas": mais_favoritas,
        "mais_acessadas": mais_acessadas,
        "recomendadas": recomendadas,
        "banners": banners,
        **interacoes(request.user),
    })


# =========================================================
# PÁGINA DE OFERTAS - USUÁRIO
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


# =========================================================
# PÁGINA DE CUPONS - USUÁRIO
# =========================================================

def cupons(request):
    lista = cupons_ativos_qs().order_by("data_validade")
    return render(request, "plataforma/cupons.html", {
        "cupons": lista,
        "total_cupons": lista.count(),
        **interacoes(request.user),
    })


# =========================================================
# PÁGINA DE FAVORITOS - USUÁRIO
# =========================================================

@login_required
def favoritos(request):
    ofertas_favoritas = (
        ofertas_ativas_qs()
        .filter(favoritos__usuario=request.user)
        .order_by("-favoritos__criado_em")
    )
    cupons_favoritos = (
        Cupom.objects
        .filter(favoritoscupons__usuario=request.user)
        .select_related("loja")
        .order_by("-favoritoscupons__criado_em")
    )
    return render(request, "plataforma/favoritos.html", {
        "ofertas_favoritas": ofertas_favoritas,
        "cupons_favoritos": cupons_favoritos,
        **interacoes(request.user),
    })


#########################################################
# INTERAÇÕES DO USUÁRIO (VOTOS / FAVORITOS / CLICKS)
#########################################################

# =========================================================
# CLICKS E CÓPIAS
# =========================================================

@require_POST
def registrar_copia_cupom(request, pk):
    """Conta uma cópia do cupom (usuário logado ou anônimo)."""
    cupom = get_object_or_404(Cupom, pk=pk)

    usuario = request.user if request.user.is_authenticated else None
    ClickCupom.objects.create(usuario=usuario, cupom=cupom)

    return JsonResponse({"usos": cupom.clicks_registros_cupons.count()})


@require_GET
def ir_para_oferta(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk)

    usuario = request.user if request.user.is_authenticated else None
    ClickOferta.objects.create(usuario=usuario, oferta=oferta)

    return redirect(oferta.link_afiliado)


# =========================================================
# VOTOS
# =========================================================

@require_POST
def votar_oferta(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    oferta = get_object_or_404(Oferta, pk=pk)

    voto, criado = Voto.objects.get_or_create(usuario=request.user, oferta=oferta)
    if not criado:
        voto.delete()

    voltar = request.META.get("HTTP_REFERER", "/")
    return redirect(f"{voltar}#oferta-{oferta.pk}")


# =========================================================
# FAVORITOS (AÇÕES)
# =========================================================

@require_POST
def favoritar_oferta(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    oferta = get_object_or_404(Oferta, pk=pk)

    favorito, criado = Favorito.objects.get_or_create(usuario=request.user, oferta=oferta)
    if not criado:
        favorito.delete()

    voltar = request.META.get("HTTP_REFERER", "/")
    return redirect(f"{voltar}#oferta-{oferta.pk}")


@require_POST
def favoritar_cupom(request, pk):
    if not request.user.is_authenticated:
        return redirect("login")

    cupom = get_object_or_404(Cupom, pk=pk)

    favorito, criado = FavoritoCupom.objects.get_or_create(usuario=request.user, cupom=cupom)
    if not criado:
        favorito.delete()

    voltar = request.META.get("HTTP_REFERER", "/")
    return redirect(f"{voltar}#cupom-{cupom.pk}")


#########################################################
# LOGIN E CADASTRO
#########################################################

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

        form.errors.pop('sexo', None)
        form.errors.pop('password1', None)
        form.errors.pop('password2', None)

        campos_etapa1 = ['username', 'email', 'telefone', 'data_nascimento']
        if not any(campo in form.errors for campo in campos_etapa1):
            request.session['cadastro'] = {
                campo: request.POST.get(campo) for campo in campos_etapa1
            }
            return redirect("cadastro_etapa2")
    else:
        dados_salvos = request.session.get('cadastro', None)
        form = CadastroForm(initial=dados_salvos)

    return render(request, TEMPLATE_CADASTRO, {"form": form})


def cadastro_etapa2(request):
    if request.method == "POST":
        dados_completos = request.session['cadastro'].copy()

        dados_completos.update(request.POST.dict())

        form = CadastroForm(dados_completos)
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("login")
    else:
        form = CadastroForm()
    return render(request, TEMPLATE_CADASTRO_ETAPA2, {"form": form})


#########################################################
# PAINEL ADMINISTRATIVO
#########################################################

# =========================================================
# DASHBOARD
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
        "total_clicks": Oferta.objects.aggregate(total=Sum("clicks_registros"))["total"] or 0,
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


# =========================================================
# LISTAGENS (ADM)
# =========================================================

@staff_member_required
def adm_usuarios(request):
    busca = request.GET.get('q', '').strip()
    usuarios = UsuarioReal.objects.order_by("-date_joined")

    if busca:
        usuarios = usuarios.filter(
            Q(username__icontains=busca) |
            Q(email__icontains=busca) |
            Q(telefone__icontains=busca)
        )
    paginator = Paginator(usuarios, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "plataforma/adm/usuarios_adm.html", {"usuarios": usuarios, "page_obj": page_obj, "eh_superadmin": request.user.is_superuser,})


@staff_member_required
def ofertas_adm(request):
    busca = request.GET.get('q', '').strip()
    lista = (
        Oferta.objects
        .select_related("loja", "categoria", "cupom")
        .order_by("-criado_em")
    )

    if busca:
        lista = lista.filter(nome_produto__icontains=busca)

    paginator = Paginator(lista, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "plataforma/adm/ofertas_adm.html", {"ofertas": page_obj, "page_obj": page_obj})


@staff_member_required
def lojas_adm(request):
    busca = request.GET.get('q', '').strip()
    lojas = LojaParceira.objects.all().order_by('nome')

    if busca:
        lojas = lojas.filter(nome__icontains=busca)

    paginator = Paginator(lojas, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'lojas': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'plataforma/adm/lojas_adm.html', context)


@staff_member_required
def categorias_adm(request):
    busca = request.GET.get('q', '').strip()
    categorias = Categoria.objects.order_by("nome")

    if busca:
        categorias = categorias.filter(nome__icontains=busca)

    paginator = Paginator(categorias, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "plataforma/adm/categorias_adm.html", {"categorias": page_obj, "page_obj": page_obj})


@staff_member_required
def cupons_adm(request):
    busca = request.GET.get('q', '').strip()
    cupons = (
        Cupom.objects
        .select_related("loja")
        .annotate(total_usos=Count("clicks_registros_cupons"))
        .order_by("-data_validade")
    )
    if busca:
        cupons = cupons.filter(codigo__icontains=busca)
    paginator = Paginator(cupons, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, "plataforma/adm/cupons_adm.html", {"cupons": page_obj, "page_obj": page_obj})


#########################################################
# CRUD (ADM)
#########################################################

# =========================================================
# CRUD DE OFERTAS
# =========================================================

# --- Versões antigas (editar_oferta é sobrescrita mais abaixo) ---
def cadastrar_oferta(request):
    return render(request, "plataforma/adm/forms/form_oferta.html")


def editar_oferta(request, id):
    oferta = Oferta.objects.get(id=id)
    return render(request, "plataforma/adm/forms/form_oferta.html", {"oferta": oferta})


# --- Versões ativas ---
@staff_member_required
def criar_oferta(request):
    lojas = LojaParceira.objects.all()
    categorias = Categoria.objects.all()
    cupons = Cupom.objects.all()

    if request.method == "POST":
        form = OfertaForm(request.POST, request.FILES)

        if form.is_valid():
            oferta = form.save()
            messages.success(
                request,
                f'Oferta "{oferta.nome_produto}" cadastrada com sucesso!'
            )
            return redirect("ofertas_adm")
    else:
        form = OfertaForm()

    return render(request, "plataforma/adm/forms/form_oferta.html", {
        "form": form,
        "lojas": lojas,
        "categorias": categorias,
        "cupons": cupons,
        "modo_edicao": False
    })


@staff_member_required
def editar_oferta(request, id):
    lojas = LojaParceira.objects.all()
    categorias = Categoria.objects.all()
    cupons = Cupom.objects.all()

    oferta = get_object_or_404(Oferta, id=id)

    if request.method == "POST":
        form = OfertaForm(
            request.POST,
            request.FILES,
            instance=oferta
        )

        if form.is_valid():
            oferta = form.save()
            messages.success(
                request,
                f'Oferta "{oferta.nome_produto}" atualizada com sucesso!'
            )
            return redirect("ofertas_adm")

    else:
        form = OfertaForm(instance=oferta)

    return render(request, "plataforma/adm/forms/form_oferta.html", {
        "form": form,
        "oferta": oferta,
        "lojas": lojas,
        "categorias": categorias,
        "cupons": cupons,
        "modo_edicao": True,
    })


@staff_member_required
@require_POST
def excluir_oferta(request, id):
    oferta = get_object_or_404(Oferta, id=id)
    nome = oferta.nome_produto
    oferta.delete()

    messages.success(request, f'Oferta "{nome}" excluída com sucesso!')
    return redirect("ofertas_adm")


# =========================================================
# CRUD CATEGORIAS
# =========================================================

# --- Versões antigas (editar_categoria é sobrescrita mais abaixo) ---
def cadastrar_categoria(request):
    return render(request, "plataforma/adm/forms/form_categoria.html")


def editar_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    return render(request, "plataforma/adm/forms/form_categoria.html", {"categoria": categoria})


# --- Versões ativas ---
@staff_member_required
def criar_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" cadastrada com sucesso!')
            return redirect("categorias_adm")
    else:
        form = CategoriaForm()

    return render(request, "plataforma/adm/forms/form_categoria.html",{"form": form})


@staff_member_required
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)

    if request.method == "POST":
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
            return redirect("categorias_adm")
    else:
        form = CategoriaForm(instance=categoria)

    return render(request, "plataforma/adm/forms/form_categoria.html", {
        "form": form,
        "categoria": categoria,
    })


@staff_member_required
@require_POST
def excluir_categoria(request, id):
    categoria = get_object_or_404(Categoria, pk=id)
    nome = categoria.nome
    categoria.delete()

    messages.success(request, f'Categoria "{nome}" excluída com sucesso!')
    return redirect("categorias_adm")


# =========================================================
# CRUD LOJAPARCEIRA
# =========================================================

def lojas(request):
    lojas = LojaParceira.objects.all().order_by("nome")

    return render(request, "plataforma/adm/lojas_adm.html", {"lojas": lojas})


@staff_member_required
def cadastrar_loja(request):
    if request.method == "POST":
        form = LojaParceiraForm(request.POST, request.FILES)
        if form.is_valid():
            loja = form.save()
            messages.success(request, f'Loja "{loja.nome}" cadastrada com sucesso!')
            return redirect("lojas_adm")
    else:
        form = LojaParceiraForm()

    return render(request, "plataforma/adm/forms/form_loja.html",{"form": form})


@staff_member_required
def editar_loja(request, id):
    loja = get_object_or_404(LojaParceira, pk=id)

    if request.method == "POST":
        form = LojaParceiraForm(
            request.POST,
            request.FILES,
            instance=loja
        )

        if form.is_valid():
            loja = form.save()
            messages.success(
                request,
                f'Loja "{loja.nome}" atualizada com sucesso!'
            )
            return redirect("lojas_adm")
    else:
        form = LojaParceiraForm(instance=loja)

    return render(
        request,
        "plataforma/adm/forms/form_loja.html",
        {
            "form": form,
            "loja": loja,
        }
    )


@staff_member_required
@require_POST
def excluir_loja(request, id):
    loja = get_object_or_404(LojaParceira, id=id)
    nome = loja.nome
    loja.delete()

    messages.success(request, f'Loja "{nome}" excluída com sucesso!')
    return redirect("lojas_adm")


# =========================================================
# CRUD CUPOM ADM
# =========================================================

# --- Versões antigas (editar_cupom é sobrescrita mais abaixo) ---
def cadastrar_cupom(request):
    return render(request, "plataforma/adm/forms/form_cupom.html")


def editar_cupom(request, id):
    cupom = Cupom.objects.get(id=id)
    return render(request, "plataforma/adm/forms/form_cupom.html", {"cupom": cupom})


# --- Versões ativas ---
@staff_member_required
def criar_cupom(request):
    lojas = LojaParceira.objects.all()

    if request.method == "POST":
        form = CupomForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Cupom cadastrado com sucesso!")
            return redirect("cupons_adm")
    else:
        form = CupomForm()

    return render(request, "plataforma/adm/forms/form_cupom.html", {
        "form": form,
        "lojas": lojas,
    })


@staff_member_required
def editar_cupom(request, id):
    cupom = get_object_or_404(Cupom, id=id)
    lojas = LojaParceira.objects.all()

    if request.method == "POST":
        form = CupomForm(
            request.POST,
            request.FILES,
            instance=cupom
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Cupom atualizado com sucesso!")
            return redirect("cupons_adm")
    else:
        form = CupomForm(instance=cupom)

    return render(request, "plataforma/adm/forms/form_cupom.html", {
        "form": form,
        "cupom": cupom,
        "lojas": lojas,
    })


@staff_member_required
@require_POST
def excluir_cupom(request, id):
    cupom = get_object_or_404(Cupom, id=id)
    codigo = cupom.codigo
    cupom.delete()

    messages.success(request, f'Cupom "{codigo}" excluído com sucesso!')
    return redirect("cupons_adm")


# =========================================================
# CRUD USUÁRIO
# =========================================================

def usuarios_adm(request):
    usuarios = UsuarioReal.filter(is_active=True).order_by("nome")

    return render(request, "plataforma/adm/usuarios_adm.html", {"usuarios": usuarios})


@staff_member_required
@require_POST
def alterar_permissao_usuario(request, id):
    destino = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        destino = "usuarios_adm"

    if not request.user.is_superuser:
        messages.error(request, "Apenas superadministradores podem alterar permissões.")
        return redirect(destino)

    alvo = get_object_or_404(UsuarioReal, pk=id)
    acao = request.POST.get("acao")

    if alvo.pk == request.user.pk:
        messages.error(request, "Você não pode alterar a sua própria permissão.")
    elif alvo.is_superuser:
        messages.error(request, "Superadministradores não podem ser alterados por aqui.")
    elif acao == "promover":
        if not alvo.is_active:
            messages.error(request, f'"{alvo.username}" está inativo e não pode ser promovido.')
        elif alvo.is_staff:
            messages.info(request, f'"{alvo.username}" já é administrador.')
        else:
            alvo.is_staff = True
            alvo.save(update_fields=["is_staff"])
            messages.success(request, f'"{alvo.username}" agora é administrador.')
    elif acao == "remover":
        if not alvo.is_staff:
            messages.info(request, f'"{alvo.username}" já é um usuário comum.')
        else:
            alvo.is_staff = False
            alvo.save(update_fields=["is_staff"])
            messages.success(request, f'"{alvo.username}" voltou a ser usuário comum.')
    else:
        messages.error(request, "Ação inválida.")

    return redirect(destino)