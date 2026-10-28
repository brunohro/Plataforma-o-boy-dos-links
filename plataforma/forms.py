from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioReal, Categoria, Oferta, LojaParceira, Cupom


class CadastroForm(UserCreationForm):
    class Meta:
        model = UsuarioReal
        fields = ["username", "email", "telefone", "data_nascimento", "sexo"]
        widgets = {
            "data_nascimento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Digite seu apelido"
        self.fields["email"].widget.attrs["placeholder"] = "seu@email.com"
        self.fields["telefone"].widget.attrs["placeholder"] = "Digite seu telefone"
        self.fields["password1"].widget.attrs["placeholder"] = "••••••"
        self.fields["password2"].widget.attrs["placeholder"] = "••••••"
        self.fields['sexo'].widget.attrs['class'] = 'form-select'

class OfertaForm(forms.ModelForm):
    class Meta:
        model = Oferta
        fields = ["nome_produto", "link_afiliado", "image_url", "descricao", "is_destaque", "is_relampago"]
        widgets = {
        'descricao': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nome_produto'].widget.attrs['placeholder'] = 'Ex: Tênis de corrida masculino'
        self.fields['link_afiliado'].widget.attrs['placeholder'] = 'https://...'
        self.fields['image_url'].widget.attrs['placeholder'] = 'https://...imagem.jpeg'
        self.fields['descricao'].widget.attrs['placeholder'] = 'Descrição da oferta...'

        self.fields['nome_produto'].widget.attrs['class'] = 'form-control'
        self.fields['loja_parceira'].widget.attrs['class'] = 'form-select'
        self.fields['categoria'].widget.attrs['class'] = 'form-select'
        self.fields['descricao'].widget.attrs['class'] = 'form-control'
        self.fields['link_afiliado'].widget.attrs['class'] = 'form-control'
        self.fields['image_url'].widget.attrs['class'] = 'form-control'
        self.fields['cupom'].widget.attrs['class'] = 'form-select'
        self.fields['is_destaque'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_relampago'].widget.attrs['class'] = 'form-check-input'

        self.fields['cupom'].empty_label = 'Nenhum cupom'
        self.fields['categoria'].empty_label = 'Selecione uma categoria'

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "icone_imagem"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da categoria"}),
            "icone_imagem": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

class LojaParceiraForm(forms.ModelForm):
    class Meta:
        model = LojaParceira
        fields = ["nome", "logo_imagem", "verificado"]
        widgets = {
            "logo_imagem": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["nome"].widget.attrs['placeholder'] = 'Ex: Mercado Livre'
            self.fields['logo_imagem'].widget.attrs['placeholder'] = 'https://...imagem.jpeg'
            self.fields['verificado'].widget.attrs['class'] = 'form-check-input'

class CupomForm(forms.ModelForm):
    class Meta:
        model = Cupom
        fields = ['codigo', 'descricao', 'data_validade', 'desconto', 'quantidade_usos', 'ativo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['codigo'].widget.attrs['placeholder'] = 'CODIGO'
        self.fields['descricao'].widget.attrs['placeholder'] = 'Ex: O cupom depende da condição ... para ser utilizado.'
        self.fields['data_validade'].widget.attrs['placeholder'] = 'xx/xx/xxxx'
        self.fields['desconto'].widget.attrs['placeholder'] = 'R$50,00'
        self.fields['quantidade_usos'].widget.attrs['placeholder'] = '100'
        self.fields['ativo'].widget.attrs['class'] = 'form-check-input'