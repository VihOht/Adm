from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .utils import get_finance_dataframes

# Create your views here.


@login_required
def index(request):
    # Get financial data for analysis
    user = request.user
    dataframes = get_finance_dataframes(user)

    # Initialize context with basic stats
    context = {
        "has_data": dataframes is not None
        and any(not df.empty for df in dataframes.values())
        if dataframes
        else False,
        "total_expenses": len(dataframes["expenses"])
        if dataframes and not dataframes["expenses"].empty
        else 0,
        "total_incomes": len(dataframes["incomes"])
        if dataframes and not dataframes["incomes"].empty
        else 0,
        "expense_categories_count": len(dataframes["expense_categories"])
        if dataframes and not dataframes["expense_categories"].empty
        else 0,
        "income_categories_count": len(dataframes["income_categories"])
        if dataframes and not dataframes["income_categories"].empty
        else 0,
    }

    # Generate graphs if data is available
    if context["has_data"]:
        try:
            from .graph_generator import generate_all_graphs

            graphs = generate_all_graphs(user)
            context.update(graphs)
        except Exception as e:
            print(f"Error generating graphs: {e}")
            # Add empty graph placeholders if generation fails
            context.update(
                {
                    "expense_category_graph": None,
                    "monthly_expenses_graph": None,
                    "income_expenses_graph": None,
                    "income_category_graph": None,
                    "daily_spending_graph": None,
                    "financial_heatmap_graph": None,
                }
            )

    return render(request, "finance_statistics/dashboard.html", context)
