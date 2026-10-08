from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    quantidade_ofertas_ativas = models.IntegerField(default=0)

    def __str__(self):
        return self.nome


class LojaParceira(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    logo_url = models.URLField(blank=True, null=True)
    verificado = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


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
    data_validade = models.DateTimeField()  # também em horas
    desconto = models.DecimalField(max_digits=5, decimal_places=2)
    quantidade_usos = models.IntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo


class DescontoCalculadoMixin(models.Model):
    preco_atual = models.DecimalField(max_digits=10, decimal_places=2)
    preco_anterior = models.DecimalField(max_digits=10, decimal_places=2)

    duracao_horas = models.PositiveIntegerField(
        "Duração (horas)",
        default=24,
        help_text="Por quantas horas a oferta fica no ar, a partir do cadastro.",
    )

    data_inicio = models.DateTimeField(default=timezone.now, editable=False)
    data_fim = models.DateTimeField(editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.data_inicio:
            self.data_inicio = timezone.now()
        self.data_fim = self.data_inicio + timedelta(hours=self.duracao_horas)
        super().save(*args, **kwargs)

    @property
    def desconto(self):
        if self.preco_anterior and self.preco_anterior > 0:
            valor = (self.preco_anterior - self.preco_atual) / self.preco_anterior * 100
            return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal("0.00")

    @property
    def economia(self):
        return self.preco_anterior - self.preco_atual

    @property
    def esta_ativa(self):
        return self.data_inicio <= timezone.now() <= self.data_fim

    @property
    def tempo_restante(self):
        return max(self.data_fim - timezone.now(), timedelta(0))

    def clean(self):
        super().clean()
        if self.preco_anterior is not None and self.preco_atual is not None:
            if self.preco_atual > self.preco_anterior:
                raise ValidationError(
                    {"preco_atual": "O preço atual não pode ser maior que o preço anterior."}
                )

class Promocao(DescontoCalculadoMixin):
    loja = models.ForeignKey(
        LojaParceira,
        on_delete=models.CASCADE,  # apagar a loja apaga as promoções dela; categoria/cupom não
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
        default=None,
    )
    nome_produto = models.CharField(max_length=100)
    link_afiliado = models.URLField()
    is_destaque = models.BooleanField(default=False)
    is_relampago = models.BooleanField(default=False)
    imagem_url = models.URLField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome_produto


class Oferta(DescontoCalculadoMixin):
    loja = models.ForeignKey(
        LojaParceira,
        on_delete=models.CASCADE,
        related_name="ofertas",
    )
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
    nome_produto = models.CharField(max_length=100)
    link_afiliado = models.URLField()
    is_destaque = models.BooleanField(default=False)
    is_relampago = models.BooleanField(default=False)
    image_url = models.URLField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    votos = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    def __str__(self):
        return self.nome_produto


class Favorito(models.Model):
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

    def __str__(self):
        return f"{self.usuario} - {self.oferta}"


class Voto(models.Model):
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

    def __str__(self):
        return f"{self.usuario} - {self.oferta}"