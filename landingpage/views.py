from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# Create your views here.


@login_required
def index(request):
    """Home page view"""
    return render(request, "landingpage/index.html")


@login_required
def test_messages(request):
    """Test view for demonstrating toast messages"""
    messages.success(request, "Operação realizada com sucesso!")
    messages.info(request, "Informação importante para você.")
    messages.warning(request, "Atenção: Esta é uma mensagem de aviso.")
    messages.error(request, "Erro: Algo deu errado!")
    return redirect("landingpage")
