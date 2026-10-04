from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class Administrador(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_administrador",
    )

    def __str__(self):
        return self.usuario.username

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    quantidade_ofertas_ativas = models.IntegerField(default=0)


class LojaParceira(models.Model):
    nome = models.CharField(max_length=100, unique=True)


class Cupom(models.Model):
    loja = models.ForeignKey(
        LojaParceira,
        on_delete=models.CASCADE,
        related_name="cupons",
        null=True,
        blank=True,
    )
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField()
    data_validade = models.DateField()
    desconto = models.DecimalField(max_digits=5, decimal_places=2)
    quantidade_usos = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo


class Promocao(models.Model):
    loja = models.ForeignKey(
        LojaParceira,
        on_delete=models.CASCADE,          #se apagar a lojas, as promoções ligadas a ela deixam de existir, o mesmo não acontece se apagar categoria ou cumpom
        related_name="promocoes",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promocoes",
    )
    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promocoes",
    )
    nome_produto = models.CharField(max_length=100)
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2)
    preco_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.DecimalField(max_digits=5, decimal_places=2)
    link_afiliado = models.URLField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    is_destaque = models.BooleanField(default=False)
    is_relampago = models.BooleanField(default=False)

class loja(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    verificado = models.BooleanField(default=True)
    def __str__(self):
        return self.nome

class Oferta(models.Model):
    loja = models.ForeignKey(
        loja,
        on_delete=models.CASCADE,
        related_name="ofertas",
    )
    nome_produto = models.CharField(max_length=100)
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2)
    preco_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.DecimalField(max_digits=5, decimal_places=2)
    link_afiliado = models.URLField()
    data_inicio = models.DateField()
    data_fim = models.DateField()
    is_destaque = models.BooleanField(default=False)
    is_relampago = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True, null=True)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ofertas",
    )
    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ofertas",
    )
    image_url = models.URLField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    votos = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    def desconto_percentual(self):
        if self.preco_anterior > 0:
            return round((self.preco_anterior - self.preco_atual) / self.preco_anterior * 100, 2)
        return 0
    def __str__(self):
        return self.nome_produto

class favorito(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="favoritos",
    )
    oferta = models.ForeignKey(
        Oferta,
        on_delete=models.CASCADE,
        related_name="favoritos",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "oferta"],
                name="unique_favorito",
            ),
        ]
        indexes = (
            models.Index(fields=["usuario", "oferta"], name="favorito_index"),
        )

    def __str__(self):
        return f"{self.usuario} - {self.oferta}"

class voto(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="votos",
    )

    oferta = models.ForeignKey(
        Oferta,
        on_delete=models.CASCADE,
        related_name="votos_registros",
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "oferta"],
                name="unique_voto",
            ),
        ]

        indexes = (
            models.Index(
                fields=["usuario", "oferta"],
                name="voto_index",
            ),
        )

    def __str__(self):
        return f"{self.usuario} - {self.oferta}"

