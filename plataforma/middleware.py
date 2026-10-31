from django.utils import timezone

from .models import Visita

# Caminhos que não contam como visita (painel, arquivos e ações)
PREFIXOS_IGNORADOS = ("/adm", "/admin", "/static", "/media", "/favicon", "/ir/")


class RegistrarVisitaMiddleware:
    """Registra no máximo uma visita por sessão a cada dia, em páginas públicas."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._registrar(request, response)
        except Exception:
            # Nunca derrubar o site por causa da estatística
            pass
        return response

    def _registrar(self, request, response):
        if request.method != "GET" or response.status_code != 200:
            return
        if request.path.startswith(PREFIXOS_IGNORADOS):
            return
        if not hasattr(request, "session"):
            return

        hoje = timezone.localdate().isoformat()
        if request.session.get("visita_registrada") == hoje:
            return

        usuario = request.user if request.user.is_authenticated else None
        Visita.objects.create(usuario=usuario)
        request.session["visita_registrada"] = hoje
