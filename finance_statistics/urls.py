from django.urls import path

from . import views

app_name = "finance_statistics"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("calendar/", views.calendar_view, name="calendar"),
    path(
        "ajax/day-transactions/",
        views.day_transactions_ajax,
        name="day_transactions_ajax",
    ),
    # AJAX graph endpoints
    path(
        "ajax/expense-category-graph/",
        views.ajax_expense_category_graph,
        name="ajax_expense_category_graph",
    ),
    path(
        "ajax/monthly-expenses-graph/",
        views.ajax_monthly_expenses_graph,
        name="ajax_monthly_expenses_graph",
    ),
    path(
        "ajax/income-expenses-graph/",
        views.ajax_income_expenses_graph,
        name="ajax_income_expenses_graph",
    ),
    path(
        "ajax/income-category-graph/",
        views.ajax_income_category_graph,
        name="ajax_income_category_graph",
    ),
    path(
        "ajax/daily-spending-graph/",
        views.ajax_daily_spending_graph,
        name="ajax_daily_spending_graph",
    ),
    path(
        "ajax/financial-heatmap-graph/",
        views.ajax_financial_heatmap_graph,
        name="ajax_financial_heatmap_graph",
    ),
]
