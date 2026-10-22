from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioReal


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