from decimal import Decimal

from django.contrib import admin
from django.db.models import DecimalField, ExpressionWrapper, F
from django.utils import timezone

from .models import (
    Categoria,
    Cupom,
    Favorito,
    LojaParceira,
    Oferta,
    Promocao,
    Usuario,
    Voto,
)


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


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "data_nascimento",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "quantidade_ofertas_ativas")
    search_fields = ("nome",)


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
        "quantidade_usos",
        "ativo",
    )
    list_filter = ("ativo", "loja", "data_validade")
    search_fields = ("codigo", "descricao", "loja__nome")
    ordering = ("-data_validade",)


@admin.register(Promocao)
class PromocaoAdmin(DescontoAdminMixin, admin.ModelAdmin):
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
        "loja__nome",
        "categoria__nome",
        "cupom__codigo",
    )
    readonly_fields = ("desconto_exibido",)
    ordering = ("-data_inicio",)


@admin.register(Oferta)
class OfertaAdmin(DescontoAdminMixin, admin.ModelAdmin):
    list_display = (
        "nome_produto",
        "loja",
        "categoria",
        "preco_atual",
        "preco_anterior",
        "desconto_exibido",
        "ativa",
        "is_destaque",
        "is_relampago",
        "votos",
        "clicks",
        "criado_em",
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
    readonly_fields = ("desconto_exibido", "criado_em", "votos", "clicks")
    ordering = ("-criado_em",)


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "oferta", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("usuario__username", "usuario__email", "oferta__nome_produto")
    readonly_fields = ("criado_em",)


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "oferta", "criado_em")
    list_filter = ("criado_em",)
    search_fields = ("usuario__username", "usuario__email", "oferta__nome_produto")
    readonly_fields = ("criado_em",)


admin.site.site_header = "Boydoslinks • Administração"
admin.site.site_title = "Boydoslinks"
admin.site.index_title = "Painel de Administração"