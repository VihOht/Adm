import os
import sys

import django
import pandas as pd

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Adm.settings")
django.setup()

from finance_manager.models import ExpenseCategory, Expenses, IncomeCategorys, Incomes


def get_finance_dataframes(user):
    """
    Get all financial data as pandas DataFrames
    """
    try:
        expenses_values = Expenses.objects.filter(user__email=user).values()
        incomes_values = Incomes.objects.filter(user__email=user).values()
        expense_category_values = ExpenseCategory.objects.filter(
            user__email=user
        ).values()
        income_categorys_values = IncomeCategorys.objects.filter(
            user__email=user
        ).values()

        df_expenses = pd.DataFrame(expenses_values)
        df_incomes = pd.DataFrame(incomes_values)
        df_expense_categories = pd.DataFrame(expense_category_values)
        df_income_categories = pd.DataFrame(income_categorys_values)

        return {
            "expenses": df_expenses,
            "incomes": df_incomes,
            "expense_categories": df_expense_categories,
            "income_categories": df_income_categories,
        }
    except Exception as e:
        print(f"Error accessing database: {e}")
        return None
