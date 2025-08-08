from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from finance_manager.models import Expenses, Incomes

# Create your views here.


@login_required
def index(request):
    """Home page view"""
    total_expenses = sum([x.amount for x in Expenses.objects.filter(user=request.user)])
    total_incomes = sum([x.amount for x in Incomes.objects.filter(user=request.user)])
    total_amount = total_incomes - total_expenses

    context = {
        "total_amount": f"{total_amount // 100},{total_amount % 100:02n}",
        "well_amount": True if total_amount >= 0 else False,
    }

    return render(request, "landingpage/index.html", context)


@login_required
def test_messages(request):
    """Test view for demonstrating toast messages"""
    messages.success(request, "Operação realizada com sucesso!")
    messages.info(request, "Informação importante para você.")
    messages.warning(request, "Atenção: Esta é uma mensagem de aviso.")
    messages.error(request, "Erro: Algo deu errado!")
    return redirect("landingpage")
