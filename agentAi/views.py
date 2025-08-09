import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from agentAi.utils import generate_response
from finance_manager.models import Expenses, Incomes


def index(request):
    return render(request, "agentAi/index.html")


@require_POST
@login_required
def get_response(request):
    try:
        data = json.loads(request.body)
        prompt = "You are a finance manager, you have acesse to the most data informations about expenses and incomes of the user. Your objective is to aid him managing their finance and help them with helpful brief advices (only when he ask), try to keep it as objective as possible"
        expenses = [
            [x.category.name if x.category else "no category", x.amount, x.spent_at]
            for x in Expenses.objects.filter(user=request.user)
        ]
        incomes = [
            [x.category.name if x.category else "no category", x.amount, x.received_at]
            for x in Incomes.objects.filter(user=request.user)
        ]
        total = {"expenses": expenses, "incomes": incomes}

        df_information = "The data amount are in Cents Reais BRL, from cents to reais should be 123456 cents == R$ 1.234,56 "

        print(total)

        complete_prompt = f"{prompt}\n\n{total}\n{df_information}"

        ai_response = generate_response(data["user_message"], complete_prompt)
        return JsonResponse(
            {
                "success": True,
                "message": "Mensagem gerada com sucesso",
                "ai_response": ai_response.text,
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"Erro generating a response {e}",
            }
        )
