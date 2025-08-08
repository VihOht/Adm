from django.urls import path

from . import views

app_name = "finance_manager"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("expense/create/", views.create_expense, name="create_expense"),
    path("expense/<int:expense_id>/edit/", views.edit_expense, name="edit_expense"),
    path(
        "expense/<int:expense_id>/delete/", views.delete_expense, name="delete_expense"
    ),
    path("category/create/", views.create_category, name="create_category"),
    path("category/<int:category_id>/edit/", views.edit_category, name="edit_category"),
    path("income/create/", views.create_income, name="create_income"),
    path("income/<int:income_id>/edit/", views.edit_income, name="edit_income"),
    path("income/<int:income_id>/delete/", views.delete_income, name="delete_income"),
    path(
        "income-category/create/",
        views.create_income_category,
        name="create_income_category",
    ),
    path(
        "income_category/<int:category_id>/edit/",
        views.edit_income_category,
        name="edit_income_category",
    ),
]
