from .models import Categoria


def categorias_header(request):
    categorias = Categoria.objects.all().order_by("nome")

    return {
        "categorias_header": categorias
    }