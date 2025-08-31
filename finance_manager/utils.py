from typing import Literal

from finance_manager.models import (
    ExpenseCategory,
    Expenses,
    IncomeCategorys,
    Incomes,
)


def get_user_financial_data(
    request,
) -> dict[
    Literal["expenses", "incomes", "expense_categories", "income_categories"], list
]:
    """
    Retrieve the user's financial data including expenses, incomes, expense categories, and income categories.
    Returns a dictionary with lists of the respective data.
    """
    # Get user's financial data
    expenses = [
        [
            x.id,
            x.category.name if x.category else "no category",
            x.amount,
            x.description,
            x.detailed_description,
            x.spent_at,
        ]
        for x in Expenses.objects.filter(user=request.user)
    ]
    incomes = [
        [
            x.id,
            x.category.name if x.category else "no category",
            x.amount,
            x.description,
            x.detailed_description,
            x.received_at,
        ]
        for x in Incomes.objects.filter(user=request.user)
    ]
    expense_categories = [
        [
            x.name,
            x.description,
            x.color,
        ]
        for x in ExpenseCategory.objects.filter(user=request.user)
    ]
    income_categories = [
        [
            x.name,
            x.description,
            x.color,
        ]
        for x in IncomeCategorys.objects.filter(user=request.user)
    ]
    data: dict[
        Literal["expenses", "incomes", "expense_categories", "income_categories"], list
    ]
    data = {
        "expenses": expenses,
        "incomes": incomes,
        "expense_categories": expense_categories,
        "income_categories": income_categories,
    }
    return data


def manipulate_finance_data(request, models) -> bool:
    """
    Manipulate finance data based on the provided models.
    Each model in the models list should be a dictionary with a "type" key indicating the operation:
    - "exp": Add a new expense
    - "inc": Add a new income
    - "cat_exp": Add a new expense category
    - "cat_inc": Add a new income category
    - "edit_exp": Edit an existing expense
    - "edit_inc": Edit an existing income
    - "edit_cat_exp": Edit an existing expense category
    - "edit_cat_inc": Edit an existing income category
    - "delete_exp": Delete an expense
    - "delete_inc": Delete an income
    - "delete_cat_exp": Delete an expense category
    - "delete_cat_inc": Delete an income category
    Each model dictionary should contain the necessary fields for the operation.
    Returns True if operations were performed, False otherwise.
    """

    if models:
        for model in models:
            try:
                # Add a new expense
                if "id" in model and isinstance(model["id"], str):
                    model["id"] = int(model["id"])
                if model["type"] == "exp":
                    if not (model["category"] == "none"):
                        category = ExpenseCategory.objects.get(
                            name=model["category"],
                            user=request.user,
                        )
                    else:
                        category = None
                    Expenses.objects.create(
                        user=request.user,
                        category=category,
                        spent_at=model["spent_at"],
                        description=model["description"],
                        detailed_description=model["detailed_description"],
                        amount=model["amount"],
                    )
                # Add a new income
                elif model["type"] == "inc":
                    if not (model["category"] == "none"):
                        category = IncomeCategorys.objects.get(
                            name=model["category"],
                            user=request.user,
                        )
                    else:
                        category = None
                    Incomes.objects.create(
                        user=request.user,
                        category=category,
                        received_at=model["spent_at"],
                        description=model["description"],
                        detailed_description=model["detailed_description"],
                        amount=model["amount"],
                    )
                # Add a new expense category
                elif model["type"] == "cat_exp":
                    ExpenseCategory.objects.create(
                        user=request.user,
                        name=model["name"],
                        description=model["description"],
                        color=model["color"],
                    )
                # Add a new income category
                elif model["type"] == "cat_inc":
                    IncomeCategorys.objects.create(
                        user=request.user,
                        name=model["name"],
                        description=model["description"],
                        color=model["color"],
                    )
                # Edit an existing expense
                elif model["type"] == "edit_exp":
                    try:
                        expense = Expenses.objects.get(
                            id=model["id"], user=request.user
                        )
                        if not (model["category"] == "none"):
                            category = ExpenseCategory.objects.get(
                                name=model["category"],
                                user=request.user,
                            )
                        else:
                            category = None
                        expense.category = category
                        expense.spent_at = model["spent_at"]
                        expense.description = model["description"]
                        expense.detailed_description = model["detailed_description"]
                        expense.amount = model["amount"]
                        expense.save()
                    except Expenses.DoesNotExist:
                        print(f"Expense with id {model['id']} does not exist.")
                # Edit an existing income
                elif model["type"] == "edit_inc":
                    try:
                        income = Incomes.objects.get(id=model["id"], user=request.user)
                        if not (model["category"] == "none"):
                            category = IncomeCategorys.objects.get(
                                name=model["category"],
                                user=request.user,
                            )
                        else:
                            category = None
                        income.category = category
                        income.received_at = model["spent_at"]
                        income.description = model["description"]
                        income.detailed_description = model["detailed_description"]
                        income.amount = model["amount"]
                        income.save()
                    except Incomes.DoesNotExist:
                        print(f"Income with id {model['id']} does not exist.")
                # Edit an existing expense category
                elif model["type"] == "edit_cat_exp":
                    try:
                        category = ExpenseCategory.objects.get(
                            name=model["old_name"], user=request.user
                        )
                        category.name = model["name"]
                        category.description = model["description"]
                        category.color = model["color"]
                        category.save()
                    except ExpenseCategory.DoesNotExist:
                        print(f"ExpenseCategory with id {model['id']} does not exist.")
                # Edit an existing income category
                elif model["type"] == "edit_cat_inc":
                    try:
                        category = IncomeCategorys.objects.get(
                            name=model["old_name"], user=request.user
                        )
                        category.name = model["name"]
                        category.description = model["description"]
                        category.color = model["color"]
                        category.save()
                    except IncomeCategorys.DoesNotExist:
                        print(f"IncomeCategory with id {model['id']} does not exist.")
                # Delete an expense
                elif model["type"] == "delete_exp":
                    try:
                        expense = Expenses.objects.get(
                            id=model["id"], user=request.user
                        )
                        expense.delete()
                    except Expenses.DoesNotExist:
                        print(f"Expense with id {model['id']} does not exist.")
                # Delete an income
                elif model["type"] == "delete_inc":
                    try:
                        income = Incomes.objects.get(id=model["id"], user=request.user)
                        income.delete()
                    except Incomes.DoesNotExist:
                        print(f"Income with id {model['id']} does not exist.")
                # Delete an expense category
                elif model["type"] == "delete_cat_exp":
                    try:
                        category = ExpenseCategory.objects.get(
                            name=model["name"], user=request.user
                        )
                        category.delete()
                    except ExpenseCategory.DoesNotExist:
                        print(f"ExpenseCategory with id {model['id']} does not exist.")
                # Delete an income category
                elif model["type"] == "delete_cat_inc":
                    try:
                        category = IncomeCategorys.objects.get(
                            name=model["name"], user=request.user
                        )
                        category.delete()
                    except IncomeCategorys.DoesNotExist:
                        print(f"IncomeCategory with id {model['id']} does not exist.")
            except Exception as e:
                print(f"Error processing model {model}: {e}")
                return False
        return True
    else:
        print("No models to process.")
        return False
