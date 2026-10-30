from decimal import Decimal

from django.contrib import admin
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Q
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Banner,
    Categoria,
    ClickOferta,
    Cupom,
    Favorito,
    LojaParceira,
    Oferta,
    UsuarioReal,
    Voto,
    FavoritoCupom,
    ClickCupom,
)

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin



@admin.register(UsuarioReal)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Dados extras", {"fields": ("telefone", "data_nascimento")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Dados extras", {"fields": ("email", "telefone", "data_nascimento")}),
    )
    list_display = ("username", "email", "telefone", "is_staff")
    
class DescontoAdminMixin:
    """Mostra o desconto calculado e permite ordenar por ele na listagem."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _desconto=ExpressionWrapper(
                (F("preco_anterior") - F("preco_atual")) * Decimal("100") / F("preco_anterior"),
                output_field=DecimalField(max_digits=6, decimal_places=2),
            )
        )

    @admin.display(description="Desconto (%)", ordering="_desconto")
    def desconto_exibido(self, obj):
        return f"{obj.desconto}%"

    @admin.display(description="Ativa?", boolean=True)
    def ativa(self, obj):
        return obj.esta_ativa

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "miniatura", "ofertas_ativas")
    search_fields = ("nome",)

    def get_queryset(self, request):
        agora = timezone.now()
        return super().get_queryset(request).annotate(
            _ativas=Count(
                "ofertas",
                filter=Q(ofertas__data_inicio__lte=agora, ofertas__data_fim__gte=agora),
            )
        )

    @admin.display(description="Ícone")
    def miniatura(self, obj):
        if obj.icone_imagem:
            return format_html('<img src="{}" style="height:32px;">', obj.icone_imagem.url)
        return "-"

    @admin.display(description="Ofertas ativas", ordering="_ativas")
    def ofertas_ativas(self, obj):
        return obj._ativas


@admin.register(LojaParceira)
class LojaParceiraAdmin(admin.ModelAdmin):
    list_display = ("nome", "verificado")
    list_filter = ("verificado",)
    search_fields = ("nome",)


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "loja",
        "desconto",
        "data_validade",
        "ativo",
    )
    list_filter = ("ativo", "loja", "data_validade")
    search_fields = ("codigo", "descricao", "loja__nome")
    ordering = ("-data_validade",)


@admin.register(Oferta)
class OfertaAdmin(DescontoAdminMixin, admin.ModelAdmin):
    list_display = (
        "nome_produto",
        "loja",
        "categoria",
        "cupom",
        "preco_atual",
        "preco_anterior",
        "desconto_exibido",
        "data_inicio",
        "data_fim",
        "ativa",
        "is_destaque",
        "is_relampago",
        "criado_em",
        "total_votos",
        "total_favoritos",
        "total_clicks",
    )
    list_filter = (
        "loja",
        "categoria",
        "is_destaque",
        "is_relampago",
        "data_inicio",
        "data_fim",
    )
    search_fields = (
        "nome_produto",
        "descricao",
        "loja__nome",
        "categoria__nome",
        "cupom__codigo",
    )
    readonly_fields = (
        "desconto_exibido",
        "data_inicio",
        "data_fim",
        "criado_em",
    )
    ordering = ("-criado_em",)

    @admin.display(description="Votos")
    def total_votos(self, obj):
        return obj.votos_registros.count()

    @admin.display(description="Favoritos")
    def total_favoritos(self, obj):
        return obj.favoritos.count()

    @admin.display(description="Cliques")
    def total_clicks(self, obj):
        return obj.clicks_registros.count()

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "oferta", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("usuario__apelido", "usuario__email", "oferta__nome_produto")
    readonly_fields = ("criado_em",)


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "oferta", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("usuario__username", "usuario__email", "oferta__nome_produto")
    readonly_fields = ("criado_em",)


@admin.register(ClickOferta)
class ClickOfertaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "oferta", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("usuario__username", "usuario__email", "oferta__nome_produto")
    readonly_fields = ("criado_em",)

admin.site.site_header = "Boydoslinks • Administração"
admin.site.site_title = "Boydoslinks"
admin.site.index_title = "Painel de Administração"

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "ordem",
        "ativo",
    )

    list_editable = ("ordem", "ativo")

    list_filter = ("ativo", "criado_em")

    search_fields = ("titulo", "descricao")

    ordering = ("ordem", "-criado_em")


@admin.register(ClickCupom)
class ClickCupomAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cupom", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("usuario__username", "usuario__email", "cupom__codigo")
    readonly_fields = ("criado_em",)

@admin.register(FavoritoCupom)
class FavoritoCupomAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cupom", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("usuario__username", "usuario__email", "cupom__codigo")
    readonly_fields = ("criado_em",)