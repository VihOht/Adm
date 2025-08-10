import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from finance_manager.models import ExpenseCategory, Expenses, IncomeCategorys, Incomes

# Create your views here.


@login_required
def dashboard(request):
    """Finance manager dashboard view"""
    expenses = Expenses.objects.filter(user=request.user).order_by("-spent_at")[:5]
    expenses_this_month = Expenses.objects.filter(
        user=request.user,
        spent_at__year=datetime.now().year,
        spent_at__month=datetime.now().month,
    )
    incomes = Incomes.objects.filter(user=request.user).order_by("-received_at")[:5]
    expense_categories = ExpenseCategory.objects.filter(user=request.user)
    income_categories = IncomeCategorys.objects.filter(user=request.user)

    total_expenses = sum([x.amount for x in Expenses.objects.filter(user=request.user)])
    total_incomes = sum([x.amount for x in Incomes.objects.filter(user=request.user)])

    range_of_days = "Sem gastos neste mês"
    total_expenses_this_month = 0
    daily_mean = 0
    if expenses_this_month:
        range_of_days = f"Últimos {datetime.now().day} dias"
        total_expenses_this_month = sum([x.amount for x in expenses_this_month])
        daily_mean = total_expenses_this_month // datetime.now().day

    total_amount = total_incomes - total_expenses

    return render(
        request,
        "finance_manager/dashboard.html",
        {
            "expenses": expenses,
            "incomes": incomes,
            "expense_categories": expense_categories,
            "income_categories": income_categories,
            "categories": expense_categories,  # For backward compatibility
            "total_expenses_this_month": f"{total_expenses_this_month // 100},{total_expenses_this_month % 100:02n}",
            "total_amount": f"{total_amount // 100},{total_amount % 100:02n}",
            "range_of_days": range_of_days,
            "daily_mean": f"{daily_mean // 100},{daily_mean % 100:02n}",
        },
    )


@login_required
def transactions(request):
    """Transactions list view showing all incomes and expenses"""
    # Get all user's transactions
    expenses = Expenses.objects.filter(user=request.user).order_by("-spent_at")
    incomes = Incomes.objects.filter(user=request.user).order_by("-received_at")

    # Create combined transactions list ordered by date (most recent first)
    all_transactions = []

    # Add expenses with type indicator
    for expense in expenses:
        all_transactions.append(
            {
                "type": "expense",
                "id": expense.id,
                "description": expense.description,
                "detailed_description": expense.detailed_description,
                "amount": expense.amount,
                "date": expense.spent_at,
                "category": expense.category,
                "object": expense,
            }
        )

    # Add incomes with type indicator
    for income in incomes:
        all_transactions.append(
            {
                "type": "income",
                "id": income.id,
                "description": income.description,
                "detailed_description": income.detailed_description,
                "amount": income.amount,
                "date": income.received_at,
                "category": income.category,
                "object": income,
            }
        )

    # Sort all transactions by date (most recent first)
    all_transactions.sort(key=lambda x: x["date"], reverse=True)

    # Get categories for editing
    expense_categories = ExpenseCategory.objects.filter(user=request.user)
    income_categories = IncomeCategorys.objects.filter(user=request.user)

    # Calculate totals
    total_expenses = sum([x.amount for x in expenses])
    total_incomes = sum([x.amount for x in incomes])
    balance = total_incomes - total_expenses

    # Format amounts for display
    def format_amount(amount):
        return f"{amount // 100},{amount % 100:02n}"

    return render(
        request,
        "finance_manager/transactions.html",
        {
            "expenses": expenses,
            "incomes": incomes,
            "all_transactions": all_transactions,
            "expense_categories": expense_categories,
            "income_categories": income_categories,
            "total_expenses": format_amount(total_expenses),
            "total_incomes": format_amount(total_incomes),
            "balance": format_amount(balance),
            "balance_raw": balance,
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
            try:
                category = ExpenseCategory.objects.get(
                    id=data["category_id"], user=request.user
                )
            except ExpenseCategory.DoesNotExist:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Categoria não encontrada ou não pertence ao usuário.",
                    }
                )

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
            user=request.user,
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
        category = get_object_or_404(ExpenseCategory, id=category_id, user=request.user)
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
def delete_category(request, category_id):
    """Delete an existing expense category and all related expenses via AJAX"""
    try:
        category = get_object_or_404(ExpenseCategory, id=category_id, user=request.user)

        # Count related expenses before deletion
        related_expenses_count = Expenses.objects.filter(category=category).count()

        category_name = category.name

        # Delete the category (this will cascade delete related expenses due to ForeignKey)
        category.delete()

        message = f"Categoria '{category_name}' excluída com sucesso!"
        if related_expenses_count > 0:
            message += f" {related_expenses_count} gasto(s) relacionado(s) também foram excluídos."

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "deleted_expenses_count": related_expenses_count,
            }
        )

    except ExpenseCategory.DoesNotExist:
        return JsonResponse({"success": False, "message": "Categoria não encontrada"})
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro ao excluir categoria: {str(e)}"}
        )


@login_required
@require_POST
def edit_income_category(request, category_id):
    """Edit an existing income category via AJAX"""
    try:
        category = get_object_or_404(IncomeCategorys, id=category_id, user=request.user)
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
def delete_income_category(request, category_id):
    """Delete an existing income category and all related incomes via AJAX"""
    try:
        category = get_object_or_404(IncomeCategorys, id=category_id, user=request.user)

        # Count related incomes before deletion
        related_incomes_count = Incomes.objects.filter(category=category).count()

        category_name = category.name

        # Delete the category (this will cascade delete related incomes due to ForeignKey)
        category.delete()

        message = f"Categoria de renda '{category_name}' excluída com sucesso!"
        if related_incomes_count > 0:
            message += f" {related_incomes_count} receita(s) relacionada(s) também foram excluídas."

        return JsonResponse(
            {
                "success": True,
                "message": message,
                "deleted_incomes_count": related_incomes_count,
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
                "message": f"Erro ao excluir categoria de renda: {str(e)}",
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
            try:
                category = ExpenseCategory.objects.get(
                    id=data["category_id"], user=request.user
                )
            except ExpenseCategory.DoesNotExist:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Categoria não encontrada ou não pertence ao usuário.",
                    }
                )

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
            try:
                category = IncomeCategorys.objects.get(
                    id=data["category_id"], user=request.user
                )
            except IncomeCategorys.DoesNotExist:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Categoria não encontrada ou não pertence ao usuário.",
                    }
                )

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
            user=request.user,
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
            try:
                category = IncomeCategorys.objects.get(
                    id=data["category_id"], user=request.user
                )
            except IncomeCategorys.DoesNotExist:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Categoria não encontrada ou não pertence ao usuário.",
                    }
                )

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


@login_required
def export_financial_data(request):
    """Export user's financial data as JSON file"""

    user = request.user

    # Prepare data structure
    data = {
        "exported_at": datetime.now().isoformat(),
        "username": user.username,
        "expense_categories": [],
        "income_categories": [],
        "expenses": [],
        "incomes": [],
    }

    # Export expense categories
    for category in ExpenseCategory.objects.filter(user=user):
        data["expense_categories"].append(
            {
                "name": category.name,
                "description": category.description,
                "color": category.color,
            }
        )

    # Export income categories
    for category in IncomeCategorys.objects.filter(user=user):
        data["income_categories"].append(
            {
                "name": category.name,
                "description": category.description,
                "color": category.color,
            }
        )

    # Export expenses
    for expense in Expenses.objects.filter(user=user).order_by("-spent_at"):
        data["expenses"].append(
            {
                "category": expense.category.name if expense.category else None,
                "spent_at": expense.spent_at.strftime("%Y-%m-%d"),
                "description": expense.description,
                "detailed_description": expense.detailed_description,
                "amount": expense.amount,
                "created_at": expense.created_at.isoformat(),
            }
        )

    # Export incomes
    for income in Incomes.objects.filter(user=user).order_by("-received_at"):
        data["incomes"].append(
            {
                "category": income.category.name if income.category else None,
                "received_at": income.received_at.strftime("%Y-%m-%d"),
                "description": income.description,
                "detailed_description": income.detailed_description,
                "amount": income.amount,
                "created_at": income.created_at.isoformat(),
            }
        )

    # Create HTTP response with JSON data
    response = HttpResponse(
        json.dumps(data, indent=2, ensure_ascii=False),
        content_type="application/json",
    )

    # Set download headers
    filename = f"financial_data_{user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


@login_required
@require_POST
def import_financial_data(request):
    """Import user's financial data from uploaded JSON file"""
    try:
        # Check if file was uploaded
        if "file" not in request.FILES:
            return JsonResponse(
                {"success": False, "message": "Nenhum arquivo foi enviado."}
            )

        uploaded_file = request.FILES["file"]

        # Validate file type
        if not uploaded_file.name.endswith(".json"):
            return JsonResponse(
                {"success": False, "message": "Apenas arquivos JSON são permitidos."}
            )

        # Check file size (limit to 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Arquivo muito grande. Limite máximo: 10MB.",
                }
            )

        # Read and parse JSON
        try:
            file_content = uploaded_file.read().decode("utf-8")
            data = json.loads(file_content)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Arquivo JSON inválido."})
        except UnicodeDecodeError:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Codificação do arquivo inválida. Use UTF-8.",
                }
            )

        # Validate JSON structure
        required_fields = [
            "expense_categories",
            "income_categories",
            "expenses",
            "incomes",
        ]
        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"success": False, "message": f"Campo obrigatório ausente: {field}"}
                )

        user = request.user
        clear_data = request.POST.get("clear_existing", "false").lower() == "true"

        # Import data using transaction for atomicity
        from django.db import transaction

        with transaction.atomic():
            if clear_data:
                # Clear existing data
                Expenses.objects.filter(user=user).delete()
                Incomes.objects.filter(user=user).delete()
                ExpenseCategory.objects.filter(user=user).delete()
                IncomeCategorys.objects.filter(user=user).delete()

            # Import expense categories
            expense_categories = {}
            categories_created = 0
            for cat_data in data.get("expense_categories", []):
                if not cat_data.get("name"):
                    continue

                category, created = ExpenseCategory.objects.get_or_create(
                    user=user,
                    name=cat_data["name"],
                    defaults={
                        "description": cat_data.get("description", ""),
                        "color": cat_data.get("color", "#FFFFFF"),
                    },
                )
                expense_categories[cat_data["name"]] = category
                if created:
                    categories_created += 1

            # Import income categories
            income_categories = {}
            income_categories_created = 0
            for cat_data in data.get("income_categories", []):
                if not cat_data.get("name"):
                    continue

                category, created = IncomeCategorys.objects.get_or_create(
                    user=user,
                    name=cat_data["name"],
                    defaults={
                        "description": cat_data.get("description", ""),
                        "color": cat_data.get("color", "#FFFFFF"),
                    },
                )
                income_categories[cat_data["name"]] = category
                if created:
                    income_categories_created += 1

            # Import expenses
            expenses_created = 0
            expenses_skipped = 0
            for expense_data in data.get("expenses", []):
                try:
                    category = None
                    if expense_data.get("category"):
                        category = expense_categories.get(expense_data["category"])

                    spent_at = datetime.strptime(
                        expense_data["spent_at"], "%Y-%m-%d"
                    ).date()

                    Expenses.objects.create(
                        user=user,
                        category=category,
                        spent_at=spent_at,
                        description=expense_data.get("description", ""),
                        detailed_description=expense_data.get(
                            "detailed_description", ""
                        ),
                        amount=int(expense_data.get("amount", 0)),
                    )
                    expenses_created += 1
                except (ValueError, KeyError, TypeError):
                    expenses_skipped += 1
                    continue

            # Import incomes
            incomes_created = 0
            incomes_skipped = 0
            for income_data in data.get("incomes", []):
                try:
                    category = None
                    if income_data.get("category"):
                        category = income_categories.get(income_data["category"])

                    received_at = datetime.strptime(
                        income_data["received_at"], "%Y-%m-%d"
                    ).date()

                    Incomes.objects.create(
                        user=user,
                        category=category,
                        received_at=received_at,
                        description=income_data.get("description", ""),
                        detailed_description=income_data.get(
                            "detailed_description", ""
                        ),
                        amount=int(income_data.get("amount", 0)),
                    )
                    incomes_created += 1
                except (ValueError, KeyError, TypeError):
                    incomes_skipped += 1
                    continue

        # Prepare success message
        total_created = (
            categories_created
            + income_categories_created
            + expenses_created
            + incomes_created
        )
        total_skipped = expenses_skipped + incomes_skipped

        message_parts = [
            "Importação concluída com sucesso!",
            f"✅ {categories_created} categorias de gastos",
            f"✅ {income_categories_created} categorias de receitas",
            f"✅ {expenses_created} gastos",
            f"✅ {incomes_created} receitas",
        ]

        if total_skipped > 0:
            message_parts.append(
                f"⚠️ {total_skipped} registros ignorados por dados inválidos"
            )

        return JsonResponse(
            {
                "success": True,
                "message": "\n".join(message_parts),
                "stats": {
                    "expense_categories": categories_created,
                    "income_categories": income_categories_created,
                    "expenses": expenses_created,
                    "incomes": incomes_created,
                    "total_created": total_created,
                    "total_skipped": total_skipped,
                },
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Erro durante a importação: {str(e)}"}
        )
