from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from .forms import CadastroForm, OfertaForm, CategoriaForm, LojaParceiraForm, CupomForm
from .models import Banner, Categoria, Cupom, Favorito, LojaParceira, Oferta, UsuarioReal, Voto, ClickOferta
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

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
        .annotate(
            total_votos=Count("votos_registros"),
            total_favoritos=Count("favoritos"),
            total_clicks=Count("clicks_registros"),
        )
    )
def interacoes(user):
    """Retorna as interações do usuário com as ofertas."""
    if user.is_authenticated:
        votos = Voto.objects.filter(usuario=user).values_list("oferta_id", flat=True)
        favoritos = Favorito.objects.filter(usuario=user).values_list("oferta_id", flat=True)
        return {
            "votos": set(votos),
            "favoritos": set(favoritos),
        }
    return {"votos": set(), "favoritos": set()}

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

@require_GET
def ir_para_oferta(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk)

    usuario = request.user if request.user.is_authenticated else None
    ClickOferta.objects.create(usuario=usuario, oferta=oferta)

    return redirect(oferta.link_afiliado)

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

@login_required
def favoritos(request):
    lista = (
        ofertas_ativas_qs()
        .filter(favoritos__usuario=request.user)
        .order_by("-favoritos__criado_em")
    )
    return render(request, "plataforma/favoritos.html", {"ofertas": lista, **interacoes(request.user)})
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
        "mais_votadas": mais_votadas,
        "mais_favoritas": mais_favoritas,
        "mais_acessadas": mais_acessadas,
        "recomendadas": recomendadas,
        "banners": banners,
        **interacoes(request.user),
    })

# =========================================================
# PÁGINA DE CUPONS - USUÁRIO
# =========================================================

def cupons(request):
    cupons = Cupom.objects.all()
    return render(request, "plataforma/cupons.html", {"cupons": cupons})

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
def criar_oferta(request):
    if request.method == "POST":
        form = OfertaForm(request.POST, request.FILES)
        if form.is_valid():
            oferta = form.save()
            messages.success(request, f'Oferta "{oferta.nome}" cadastrada com sucesso!')
            return redirect("ofertas_adm")
        else:
            form = OfertaForm()

        return render(request, "plataforma/templates/adm/ofertas_adm.html")

@staff_member_required
def editar_oferta(request, id):
    oferta = get_object_or_404(request, id=id)

    if request.method == "POST":
        form = OfertaForm(request.POST, request.FILES, instance=oferta)
        if form.is_valid():
            oferta = form.save()
            messages.success(request, f'Oferta "{oferta.nome}" atualizada com sucesso!')
            return redirect("ofertas_adm")
        else:
            form = OfertaForm(instance=oferta)

        return render(request, "form/form_ofertas.html", {
            "form": form,
            "oferta": oferta,
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
def adm_categorias(request):
    categorias = Categoria.objects.all()

    return render(request, "plataforma/adm_categorias.html", {"categorias": categorias})

@staff_member_required
def criar_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" cadastrada com sucesso!')
            return redirect("adm_categorias")
    else:
        form = CategoriaForm()

    return render(request, "plataforma/categoria_form.html",{"form": form})

@staff_member_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    if request.method == "POST":
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
            return redirect("adm_categorias")
        else:
            form = CategoriaForm(instance=categoria)
            
        return render(request, "categorias/form.html", {
            "form": form,
            "categoria": categoria,
        })

@staff_member_required
@require_POST
def excluir_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    nome = categoria.nome
    categoria.delete()

    messages.success(request, f'Categoria "{nome}" excluída com sucesso!')
    return redirect("adm_categorias")

# =========================================================
# CRUD LOJAPARCEIRA
# =========================================================
def lojas(request):
    lojas = LojaParceira.objects.all()

    return render(request, "plataforma/lojas_adm.html", {"lojas": lojas})

@staff_member_required
def criar_loja(request):
    if request.method == "POST":
        form = LojaParceiraForm(request.POST, request.FILES)
        if form.is_valid():
            loja = form.save()
            messages.success(request, f'Loja "{loja.nome}" cadastrada com sucesso!')
            return redirect("lojas_adm")
    else:
        form = LojaParceiraForm()

    return render(request, "plataforma/form_loja.html",{"form": form})

@staff_member_required
def editar_loja(request, id):
    loja = get_object_or_404(Categoria, id=id)

    if request.method == "POST":
        form = LojaParceiraForm(request.POST, request.FILES, instance=loja)
        if form.is_valid():
            loja = form.save()
            messages.success(request, f'Loja "{loja.nome}" atualizada com sucesso!')
            return redirect("lojas_adm")
        else:
            form = LojaParceiraForm(instance=loja)
            
        return render(request, "plataforma/form_lojas.html", {
            "form": form,
            "loja": loja,
        })

@staff_member_required
@require_POST
def excluir_loja(request, id):
    loja = get_object_or_404(Categoria, id=id)
    nome = loja.nome
    loja.delete()

    messages.success(request, f'Loja "{nome}" excluída com sucesso!')
    return redirect("lojas_adm")

# =========================================================
# CRUD CUPOM ADM
# =========================================================
def cupons_adm(request, id):
    cupons = Cupom.objects.all()

    return render(request, "plataforma/cupom_adm.html")

@staff_member_required
def criar_cupom(request):
    if request.method == "POST":
        form = CupomForm(request.POST, request.FILES)
        if form.is_valid():
            cupom = form.save()
            messages.success(request, f'Cupom "{cupom.nome}" cadastrado com sucesso!')
            return redirect("cupom_adm")
        else:
            form = CupomForm()
    
        return render(request, "plataforma/form_cupom.html",{"form": form})

def editar_cupom(request, id):
    cupom = get_object_or_404(Categoria, id=id)

    if request.method == "POST":
        form = CupomForm(request.POST, request.FILES, instance=cupom)
        if form.is_valid():
            cupom = form.save()
            messages.success(request, f'Cupom "{cupom.nome}" atualizado com sucesso!')
            return redirect("cupom_adm")
        else:
            form = CupomForm(instance=cupom)
            
        return render(request, "plataforma/form_cupom.html", {
            "form": form,
            "cupom": cupom,
        })

@staff_member_required
@require_POST
def excluir_cupom(request, id):
    cupom = get_object_or_404(Categoria, id=id)
    nome = cupom.nome
    cupom.delete()

    messages.success(request, f'Cupom "{nome}" excluído com sucesso!')
    return redirect("cupom_adm")

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

