from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .calendar_generator import TransactionCalendarGenerator
from .utils import get_finance_dataframes


@login_required
def dashboard_view(request):
    """Finance statistics dashboard view"""

    # Get basic counts for the stats cards
    dataframes = get_finance_dataframes(request.user)

    context = {
        "has_data": True,
        "total_expenses": len(dataframes.get("expenses", [])),
        "total_incomes": len(dataframes.get("incomes", [])),
        "expense_categories_count": len(dataframes.get("expense_categories", [])),
        "income_categories_count": len(dataframes.get("income_categories", [])),
    }

    return render(request, "finance_statistics/dashboard.html", context)


@login_required
def calendar_view(request):
    """Transaction calendar view"""
    year = request.GET.get("year", timezone.now().year)
    month = request.GET.get("month", timezone.now().month)

    try:
        year = int(year)
        month = int(month)
    except (ValueError, TypeError):
        year = timezone.now().year
        month = timezone.now().month

    # Generate calendar data
    calendar_generator = TransactionCalendarGenerator(request.user)
    calendar_data = calendar_generator.generate_calendar_data(year, month)

    # Navigation data for previous/next month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        "calendar_data": calendar_data,
        "current_year": year,
        "current_month": month,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    }

    return render(request, "finance_statistics/calendar.html", context)


@login_required
def day_transactions_ajax(request):
    """AJAX endpoint to get transactions for a specific day"""
    date = request.GET.get("date")
    if not date:
        return JsonResponse({"error": "Date parameter required"}, status=400)

    try:
        # Parse date
        year, month, day = date.split("-")
        year, month, day = int(year), int(month), int(day)
    except (ValueError, TypeError):
        return JsonResponse({"error": "Invalid date format"}, status=400)

    # Generate calendar data for the month
    calendar_generator = TransactionCalendarGenerator(request.user)
    calendar_data = calendar_generator.generate_calendar_data(year, month)

    # Find the specific day
    day_data = None
    for week in calendar_data["calendar"]:
        for day_info in week:
            if day_info.get("date") == date:
                day_data = day_info
                break
        if day_data:
            break

    if not day_data:
        return JsonResponse({"error": "Day not found"}, status=404)

    return JsonResponse(
        {
            "date": date,
            "day": day_data["day"],
            "transactions": day_data["transactions"],
            "statistics": {
                "total_transactions": day_data["transaction_count"],
                "total_expenses": day_data["expenses"],
                "total_incomes": day_data["incomes"],
                "balance": day_data["balance"],
            },
        }
    )


@login_required
def dashboard(request):
    """Finance statistics dashboard with quick loading and AJAX graphs"""
    user = request.user

    # Get basic counts for immediate display
    total_expenses = Expenses.objects.filter(user=user).count()
    total_incomes = Incomes.objects.filter(user=user).count()
    expense_categories_count = ExpenseCategory.objects.filter(user=user).count()
    income_categories_count = IncomeCategorys.objects.filter(user=user).count()

    # Check if user has data
    has_data = total_expenses > 0 or total_incomes > 0

    context = {
        "total_expenses": total_expenses,
        "total_incomes": total_incomes,
        "expense_categories_count": expense_categories_count,
        "income_categories_count": income_categories_count,
        "has_data": has_data,
        # Don't generate graphs here - they'll be loaded via AJAX
    }

    return render(request, "finance_statistics/dashboard.html", context)


@login_required
def ajax_expense_category_graph(request):
    """Generate expense category graph via AJAX"""
    try:
        user = request.user
        from .graph_generator import FinanceGraphGenerator

        generator = FinanceGraphGenerator(user)
        graph_data = generator.generate_expenses_by_category()

        return JsonResponse(
            {
                "success": True,
                "graph": graph_data,
                "has_data": graph_data is not None,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_monthly_expenses_graph(request):
    """Generate monthly expenses trend graph via AJAX"""
    try:
        user = request.user
        from .graph_generator import FinanceGraphGenerator

        generator = FinanceGraphGenerator(user)
        graph_data = generator.generate_monthly_expenses_trend()

        return JsonResponse(
            {
                "success": True,
                "graph": graph_data,
                "has_data": graph_data is not None,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_income_expenses_graph(request):
    """Generate income vs expenses comparison graph via AJAX"""
    try:
        user = request.user
        from .graph_generator import FinanceGraphGenerator

        generator = FinanceGraphGenerator(user)
        graph_data = generator.generate_income_vs_expenses()

        return JsonResponse(
            {
                "success": True,
                "graph": graph_data,
                "has_data": graph_data is not None,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_income_category_graph(request):
    """Generate income category graph via AJAX"""
    try:
        user = request.user
        from .graph_generator import FinanceGraphGenerator

        generator = FinanceGraphGenerator(user)
        graph_data = generator.generate_income_by_category()

        return JsonResponse(
            {
                "success": True,
                "graph": graph_data,
                "has_data": graph_data is not None,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_daily_spending_graph(request):
    """Generate daily spending pattern graph via AJAX"""
    try:
        user = request.user
        from .graph_generator import FinanceGraphGenerator

        generator = FinanceGraphGenerator(user)
        graph_data = generator.generate_daily_spending_pattern()

        return JsonResponse(
            {
                "success": True,
                "graph": graph_data,
                "has_data": graph_data is not None,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@login_required
def ajax_financial_heatmap_graph(request):
    """Generate financial heatmap graph via AJAX"""
    try:
        user = request.user
        from .graph_generator import FinanceGraphGenerator

        generator = FinanceGraphGenerator(user)
        graph_data = generator.generate_financial_heatmap()

        return JsonResponse(
            {
                "success": True,
                "graph": graph_data,
                "has_data": graph_data is not None,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
