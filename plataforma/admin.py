from django.contrib import admin

from .models import*


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

    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
    )

    search_fields = (
        "usuario__username",
        "usuario__email",
    )


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "quantidade_ofertas_ativas",
    )

    search_fields = (
        "nome",
    )


@admin.register(LojaParceira)
class LojaParceiraAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
    )

    search_fields = (
        "nome",
    )


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

    list_filter = (
        "ativo",
        "loja",
        "data_validade",
    )

    search_fields = (
        "codigo",
        "descricao",
        "loja__nome",
    )

    ordering = (
        "-data_validade",
    )


@admin.register(Promocao)
class PromocaoAdmin(admin.ModelAdmin):
    list_display = (
        "nome_produto",
        "loja",
        "categoria",
        "cupom",
        "preco_atual",
        "preco_anterior",
        "desconto",
        "data_inicio",
        "data_fim",
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


@admin.register(loja)
class LojaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "verificado",
        "slug",
    )

    list_filter = (
        "verificado",
    )

    search_fields = (
        "nome",
    )

    prepopulated_fields = {
        "slug": ("nome",),
    }


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = (
        "nome_produto",
        "loja",
        "categoria",
        "preco_atual",
        "preco_anterior",
        "desconto",
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

    prepopulated_fields = {
        "slug": ("nome_produto",),
    }

    readonly_fields = (
        "criado_em",
        "votos",
        "clicks",
    )

    ordering = (
        "-criado_em",
    )


@admin.register(favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "oferta",
        "criado_em",
    )

    list_filter = (
        "criado_em",
    )

    search_fields = (
        "usuario__username",
        "usuario__email",
        "oferta__nome_produto",
    )

    readonly_fields = (
        "criado_em",
    )


@admin.register(voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "oferta",
        "criado_em",
    )

    list_filter = (
        "criado_em",
    )

    search_fields = (
        "usuario__username",
        "usuario__email",
        "oferta__nome_produto",
    )

    readonly_fields = (
        "criado_em",
    )


admin.site.site_header = "Boydoslinks • Administração"
admin.site.site_title = "Boydoslinks"
admin.site.index_title = "Painel de Administração"
