from django.db import models

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_legth=100)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=20)
    dataNascimento = models.DateField()


class Administrador(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

class Promocao(models.Model):
    id = models.AutoField(primary_key=True)
    nomeProduto = models.CharField(max_length=100)
    precoAtual = models.DecimalField(max_digits=10, decimal_places=2)
    precoAnterior = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.PercentageField((precoAnterior - precoAtual) / precoAnterior * 100)
    linkAfiliado = models.URLField()
    dataInicio = models.DateField()
    dataFim = models.DateField()
    isDestaque = models.BooleanField(default=False)
    isRelampago = models.BooleanField(default=False)
    #isParaVoce = models.BooleanField(default=False)

class Cupom(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    descricao = models.TextField()
    dataValidade = models.DateField()
    desconto = models.DecimalField(max_digits=5, decimal_places=2)

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    quanidadeOfertasAtivas = models.IntegerField(default=0)

class LojaParceira(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)