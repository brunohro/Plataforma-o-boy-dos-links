from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models


class UsuarioReal(AbstractUser):
    apelido = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    sexo = models.CharField(max_length=10, choices=[("M", "Masculino"), ("F", "Feminino"), ("O", "Outro")], blank=True)

    def __str__(self):
        return self.apelido or self.username


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    icone_imagem = models.ImageField(blank=True, null=True, upload_to="categorias/")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    @property
    def contador_ofertas(self):
        agora = timezone.now()
        return self.ofertas.filter(data_inicio__lte=agora, data_fim__gte=agora).count()


class LojaParceira(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    logo_imagem = models.ImageField(blank=True, null=True, upload_to="lojas/")
    verificado = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

    class Meta: 
        verbose_name = "Loja Parceira"
        verbose_name_plural = "Lojas Parceiras"
        ordering = ["nome"]

    @property
    def contador_ofertas(self):
        agora = timezone.now()
        return self.ofertas.filter(data_inicio__lte=agora, data_fim__gte=agora).count()

    @property
    def contador_cupons(self):
        agora = timezone.now()
        return self.cupons.filter(ativo=True, data_validade__gte=agora).count()


class Cupom(models.Model):
    loja = models.ForeignKey(
        LojaParceira,
        on_delete=models.CASCADE,
        related_name="cupons",
    )
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField()
    data_validade = models.DateTimeField()
    desconto = models.DecimalField(max_digits=5, decimal_places=2)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.codigo

    class Meta:
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"
        ordering = ["-data_validade"]

    def quantidade_usos(self):
        return ClickCupom.objects.filter(cupom=self).count()


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


class Oferta(DescontoCalculadoMixin):
    loja = models.ForeignKey(
        LojaParceira,
        on_delete=models.CASCADE,
        related_name="ofertas",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
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
    image_url = models.ImageField(upload_to="ofertas/", blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    is_destaque = models.BooleanField(default=False)
    is_relampago = models.BooleanField("Oferta relâmpago", default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.nome_produto

    class Meta:
        verbose_name = "Oferta"
        verbose_name_plural = "Ofertas"
        ordering = ["-criado_em"]


class Favorito(models.Model):
    usuario = models.ForeignKey(
        UsuarioReal,
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
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        ordering = ["-criado_em"]
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
        UsuarioReal,
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
        verbose_name = "Voto"
        verbose_name_plural = "Votos"
        ordering = ["-criado_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "oferta"],
                name="unique_voto",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.oferta}"

class ClickOferta(models.Model):
    usuario = models.ForeignKey(
        UsuarioReal,
        on_delete=models.CASCADE,
        related_name="clicks_ofertas",
    )
    oferta = models.ForeignKey(
        Oferta,
        on_delete=models.CASCADE,
        related_name="clicks_registros",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Click de Oferta"
        verbose_name_plural = "Clicks de Ofertas"
        ordering = ["-criado_em"]


class Banner(models.Model):
    titulo = models.CharField(max_length=100)
    imagem = models.ImageField(upload_to="banners/")
    descricao = models.TextField(blank=True, null=True)
    link = models.URLField()
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de exibição")
    criado_em = models.DateTimeField(auto_now_add=True)
    texto_botao = models.CharField(max_length=50, blank=True, null=True, default="Saiba mais", verbose_name="Texto do botão")

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banners"
        ordering = ["-criado_em"]

class FavoritoCupom(models.Model):
    usuario = models.ForeignKey(
        UsuarioReal,
        on_delete=models.CASCADE,
        related_name="favoritoscupons",
    )
    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.CASCADE,
        related_name="favoritoscupons",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favorito de Cupom"
        verbose_name_plural = "Favoritos de Cupom"
        ordering = ["-criado_em"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "cupom"],
                name="unique_favoritocupom",
            ),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.cupom}"


class ClickCupom(models.Model):
    usuario = models.ForeignKey(
        UsuarioReal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clicks_cupons",
    )
    cupom = models.ForeignKey(
        Cupom,
        on_delete=models.CASCADE,
        related_name="clicks_registros_cupons",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Click de Cupom"
        verbose_name_plural = "Clicks de Cupons"
        ordering = ["-criado_em"]