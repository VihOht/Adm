import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from finance_manager.models import ExpenseCategory, Expenses, IncomeCategorys, Incomes

# Create your views here.


@login_required
def dashboard(request):
    """Finance manager dashboard view"""
    expenses = Expenses.objects.filter(user=request.user).order_by("-spent_at")[:5]
    incomes = Incomes.objects.filter(user=request.user).order_by("-received_at")[:5]
    expense_categories = ExpenseCategory.objects.all()
    income_categories = IncomeCategorys.objects.all()

    total_expenses = sum([x.amount for x in Expenses.objects.filter(user=request.user)])
    total_incomes = sum([x.amount for x in Incomes.objects.filter(user=request.user)])

    return render(
        request,
        "finance_manager/dashboard.html",
        {
            "expenses": expenses,
            "incomes": incomes,
            "expense_categories": expense_categories,
            "income_categories": income_categories,
            "categories": expense_categories,  # For backward compatibility
            "total_expenses": f"{total_expenses // 100},{total_expenses % 100:02n}",
            "total_incomes": f"{total_incomes // 100},{total_incomes % 100:02n}",
        },
    )


@login_required
@require_POST
def create_expense(request):
    """Create a new expense via AJAX"""
    try:
        data = json.loads(request.body)

        # Get or create category
        category = None
        if data.get("category_id"):
            category = ExpenseCategory.objects.get(id=data["category_id"])

        # Convert amount from cents to integer (assuming input is in reais)
        amount_in_cents = int(float(data["amount"]) * 100)

        # Parse date
        spent_date = datetime.strptime(data["spent_at"], "%Y-%m-%d").date()

        # Create expense
        expense = Expenses.objects.create(
            user=request.user,
            category=category,
            description=data["description"],
            detailed_description=data.get("detailed_description", ""),
            amount=amount_in_cents,
            spent_at=spent_date,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Gasto adicionado com sucesso!",
                "expense_id": expense.id,
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao criar gasto: {str(e)}"}
        )


@login_required
@require_POST
def create_category(request):
    """Create a new expense category via AJAX"""
    try:
        data = json.loads(request.body)

        category = ExpenseCategory.objects.create(
            name=data["name"],
            description=data.get("description", ""),
            color=data.get("color", "#FFFFFF"),
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Categoria criada com sucesso!",
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "color": category.color,
                },
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao criar categoria: {str(e)}"}
        )


@login_required
@require_POST
def edit_category(request, category_id):
    """Edit an existing expense category via AJAX"""
    try:
        category = get_object_or_404(ExpenseCategory, id=category_id)
        data = json.loads(request.body)

        # Update category
        category.name = data["name"]
        category.description = data.get("description", "")
        category.color = data.get("color", "#FFFFFF")
        category.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Categoria atualizada com sucesso!",
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "color": category.color,
                },
            }
        )

    except ExpenseCategory.DoesNotExist:
        return JsonResponse({"success": False, "message": "Categoria não encontrada"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao atualizar categoria: {str(e)}"}
        )


@login_required
@require_POST
def edit_income_category(request, category_id):
    """Edit an existing income category via AJAX"""
    try:
        category = get_object_or_404(IncomeCategorys, id=category_id)
        data = json.loads(request.body)

        # Update category
        category.name = data["name"]
        category.description = data.get("description", "")
        category.color = data.get("color", "#FFFFFF")
        category.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Categoria de renda atualizada com sucesso!",
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "color": category.color,
                },
            }
        )

    except IncomeCategorys.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Categoria de renda não encontrada"}
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": f"Erro ao atualizar categoria de renda: {str(e)}",
            }
        )


@login_required
@require_POST
def edit_expense(request, expense_id):
    """Edit an existing expense via AJAX"""
    try:
        expense = get_object_or_404(Expenses, id=expense_id, user=request.user)
        data = json.loads(request.body)

        # Get or update category
        category = None
        if data.get("category_id"):
            category = ExpenseCategory.objects.get(id=data["category_id"])

        # Convert amount from cents to integer (assuming input is in reais)
        amount_in_cents = int(float(data["amount"]) * 100)

        # Parse date
        spent_date = datetime.strptime(data["spent_at"], "%Y-%m-%d").date()

        # Update expense
        expense.category = category
        expense.description = data["description"]
        expense.detailed_description = data.get("detailed_description", "")
        expense.amount = amount_in_cents
        expense.spent_at = spent_date
        expense.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Gasto atualizado com sucesso!",
                "expense_id": expense.id,
            }
        )

    except Expenses.DoesNotExist:
        return JsonResponse({"success": False, "message": "Gasto não encontrado"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao atualizar gasto: {str(e)}"}
        )


@login_required
@require_POST
def delete_expense(request, expense_id):
    """Delete an existing expense via AJAX"""
    try:
        expense = get_object_or_404(Expenses, id=expense_id, user=request.user)
        expense.delete()

        return JsonResponse(
            {
                "success": True,
                "message": "Gasto excluído com sucesso!",
            }
        )

    except Expenses.DoesNotExist:
        return JsonResponse({"success": False, "message": "Gasto não encontrado"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao excluir gasto: {str(e)}"}
        )


@login_required
@require_POST
def create_income(request):
    """Create a new income via AJAX"""
    try:
        data = json.loads(request.body)

        # Get or create category
        category = None
        if data.get("category_id"):
            category = IncomeCategorys.objects.get(id=data["category_id"])

        # Convert amount from cents to integer (assuming input is in reais)
        amount_in_cents = int(float(data["amount"]) * 100)

        # Parse date
        received_date = datetime.strptime(data["received_at"], "%Y-%m-%d").date()

        # Create income
        income = Incomes.objects.create(
            user=request.user,
            category=category,
            description=data["description"],
            detailed_description=data.get("detailed_description", ""),
            amount=amount_in_cents,
            received_at=received_date,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Receita adicionada com sucesso!",
                "income_id": income.id,
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao criar receita: {str(e)}"}
        )


@login_required
@require_POST
def create_income_category(request):
    """Create a new income category via AJAX"""
    try:
        data = json.loads(request.body)

        category = IncomeCategorys.objects.create(
            name=data["name"],
            description=data.get("description", ""),
            color=data.get("color", "#FFFFFF"),
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Categoria de receita criada com sucesso!",
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "color": category.color,
                },
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao criar categoria: {str(e)}"}
        )


@login_required
@require_POST
def edit_income(request, income_id):
    """Edit an existing income via AJAX"""
    try:
        income = get_object_or_404(Incomes, id=income_id, user=request.user)
        data = json.loads(request.body)

        # Get or update category
        category = None
        if data.get("category_id"):
            category = IncomeCategorys.objects.get(id=data["category_id"])

        # Convert amount from cents to integer (assuming input is in reais)
        amount_in_cents = int(float(data["amount"]) * 100)

        # Parse date
        received_date = datetime.strptime(data["received_at"], "%Y-%m-%d").date()

        # Update income
        income.category = category
        income.description = data["description"]
        income.detailed_description = data.get("detailed_description", "")
        income.amount = amount_in_cents
        income.received_at = received_date
        income.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Receita atualizada com sucesso!",
                "income_id": income.id,
            }
        )

    except Incomes.DoesNotExist:
        return JsonResponse({"success": False, "message": "Receita não encontrada"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao atualizar receita: {str(e)}"}
        )


@login_required
@require_POST
def delete_income(request, income_id):
    """Delete an existing income via AJAX"""
    try:
        income = get_object_or_404(Incomes, id=income_id, user=request.user)
        income.delete()

        return JsonResponse(
            {
                "success": True,
                "message": "Receita excluída com sucesso!",
            }
        )

    except Incomes.DoesNotExist:
        return JsonResponse({"success": False, "message": "Receita não encontrada"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao excluir receita: {str(e)}"}
        )
