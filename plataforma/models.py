from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    data_nascimento = models.DateField(null=True, blank=True)

    def __str__(self):
        pass


class Administrador(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil_administrador",
    )


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