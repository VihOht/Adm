import base64
import io
import os
import sys

import django
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Adm.settings")
django.setup()

from finance_statistics.utils import get_finance_dataframes


class FinanceGraphGenerator:
    def __init__(self, user):
        self.dataframes = get_finance_dataframes(user)
        plt.style.use("seaborn-v0_8")
        sns.set_palette("husl")

    def _fig_to_base64(self, fig):
        """Convert matplotlib figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(
            buffer,
            format="png",
            bbox_inches="tight",
            dpi=150,
            facecolor="white",
            edgecolor="none",
        )
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        buffer.close()
        plt.close(fig)
        return image_base64

    def generate_expenses_by_category(self):
        """Generate pie chart for expenses by category"""
        if not self.dataframes or self.dataframes["expenses"].empty:
            return None

        expenses_df = self.dataframes["expenses"]
        categories_df = self.dataframes["expense_categories"]

        # Merge expenses with categories
        merged = expenses_df.merge(
            categories_df, left_on="category_id", right_on="id", suffixes=("", "_cat")
        )

        # Group by category and sum amounts
        category_totals = merged.groupby("name")["amount"].sum()

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(category_totals)))

        wedges, texts, autotexts = ax.pie(
            category_totals.values,
            labels=category_totals.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
        )

        ax.set_title("Gastos por Categoria", fontsize=16, fontweight="bold", pad=20)

        # Add value labels
        for i, (category, amount) in enumerate(category_totals.items()):
            autotexts[i].set_text(f"R$ {amount / 100:.2f}\n({autotexts[i].get_text()})")

        return self._fig_to_base64(fig)

    def generate_monthly_expenses_trend(self):
        """Generate line chart for monthly expenses trend"""
        if not self.dataframes or self.dataframes["expenses"].empty:
            return None

        expenses_df = self.dataframes["expenses"].copy()
        expenses_df["spent_at"] = pd.to_datetime(expenses_df["spent_at"])
        expenses_df["month_year"] = expenses_df["spent_at"].dt.to_period("M")

        monthly_totals = expenses_df.groupby("month_year")["amount"].sum()

        fig, ax = plt.subplots(figsize=(12, 6))

        x_labels = [str(period) for period in monthly_totals.index]
        y_values = monthly_totals.values / 100  # Convert to reais

        ax.plot(x_labels, y_values, marker="o", linewidth=2, markersize=8)
        ax.fill_between(x_labels, y_values, alpha=0.3)

        ax.set_title(
            "Tendência Mensal de Gastos", fontsize=16, fontweight="bold", pad=20
        )
        ax.set_xlabel("Mês/Ano", fontsize=12)
        ax.set_ylabel("Valor (R$)", fontsize=12)
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        return self._fig_to_base64(fig)

    def generate_income_vs_expenses(self):
        """Generate bar chart comparing income vs expenses by month"""
        if not self.dataframes:
            return None

        expenses_df = self.dataframes["expenses"]
        incomes_df = self.dataframes["incomes"]

        if expenses_df.empty and incomes_df.empty:
            return None

        # Prepare monthly data
        monthly_expenses = pd.Series(dtype="float64")
        monthly_incomes = pd.Series(dtype="float64")

        if not expenses_df.empty:
            expenses_df = expenses_df.copy()
            expenses_df["spent_at"] = pd.to_datetime(expenses_df["spent_at"])
            expenses_df["month_year"] = expenses_df["spent_at"].dt.to_period("M")
            monthly_expenses = expenses_df.groupby("month_year")["amount"].sum() / 100

        if not incomes_df.empty:
            incomes_df = incomes_df.copy()
            incomes_df["received_at"] = pd.to_datetime(incomes_df["received_at"])
            incomes_df["month_year"] = incomes_df["received_at"].dt.to_period("M")
            monthly_incomes = incomes_df.groupby("month_year")["amount"].sum() / 100

        # Get all months from both datasets
        all_months = pd.Index([])
        if not monthly_expenses.empty:
            all_months = all_months.union(monthly_expenses.index)
        if not monthly_incomes.empty:
            all_months = all_months.union(monthly_incomes.index)

        if all_months.empty:
            return None

        # Reindex both series to have all months
        monthly_expenses = monthly_expenses.reindex(all_months, fill_value=0)
        monthly_incomes = monthly_incomes.reindex(all_months, fill_value=0)

        # Create figure with more space
        fig, ax = plt.subplots(figsize=(16, 10))

        # Add extra margin at the top for the summary text
        plt.subplots_adjust(top=0.85, bottom=0.15, left=0.1, right=0.95)

        # Prepare data for grouped bar chart
        months = [str(month) for month in all_months]
        x_pos = range(len(months))
        width = 0.35  # Increased width for better visibility

        # Create bars
        income_bars = ax.bar(
            [x - width / 2 for x in x_pos],
            monthly_incomes.values,
            width,
            label="Receitas",
            color="#10b981",
            alpha=0.8,
            edgecolor="white",
            linewidth=0.5,
        )
        expense_bars = ax.bar(
            [x + width / 2 for x in x_pos],
            monthly_expenses.values,
            width,
            label="Gastos",
            color="#ef4444",
            alpha=0.8,
            edgecolor="white",
            linewidth=0.5,
        )

        # Calculate max value for proper spacing
        max_value = max(
            max(monthly_incomes) if len(monthly_incomes) > 0 else 0,
            max(monthly_expenses) if len(monthly_expenses) > 0 else 0,
        )

        # Add value labels on bars with better positioning
        for bars, values in [
            (income_bars, monthly_incomes.values),
            (expense_bars, monthly_expenses.values),
        ]:
            for bar, value in zip(bars, values):
                if value > 0:  # Only show label if there's a value
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        value + max_value * 0.02,  # Better spacing from bar top
                        f"R$ {value:.0f}",
                        ha="center",
                        va="bottom",
                        fontsize=10,
                        fontweight="bold",
                        rotation=0,
                    )

        # Calculate monthly balance and add balance line with better styling
        monthly_balance = monthly_incomes - monthly_expenses
        ax.plot(
            x_pos,
            monthly_balance.values,
            color="#6366f1",
            marker="o",
            linewidth=3,
            markersize=8,
            label="Saldo Mensal",
            alpha=0.9,
            markerfacecolor="white",
            markeredgecolor="#6366f1",
            markeredgewidth=2,
        )

        # Add zero line for reference
        ax.axhline(y=0, color="black", linestyle="--", alpha=0.5, linewidth=1)

        # Set Y-axis limits with padding
        y_max = max_value * 1.25  # Add 25% padding at top
        y_min = min(monthly_balance.min() if len(monthly_balance) > 0 else 0, 0) * 1.1
        ax.set_ylim(y_min, y_max)

        # Formatting
        ax.set_title(
            "Receitas vs Gastos por Mês", fontsize=18, fontweight="bold", pad=30
        )
        ax.set_xlabel("Mês/Ano", fontsize=14, fontweight="bold")
        ax.set_ylabel("Valor (R$)", fontsize=14, fontweight="bold")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(months, rotation=45, ha="right", fontsize=11)

        # Improve legend positioning and styling
        ax.legend(
            loc="upper left",
            frameon=True,
            fancybox=True,
            shadow=True,
            fontsize=12,
            bbox_to_anchor=(0.02, 0.98),
        )
        ax.grid(True, alpha=0.3, axis="y", linestyle="-", linewidth=0.5)

        # Add overall summary text at the top with better positioning
        total_income = monthly_incomes.sum()
        total_expense = monthly_expenses.sum()
        overall_balance = total_income - total_expense
        balance_color = "#10b981" if overall_balance >= 0 else "#ef4444"

        # Place summary text above the plot area
        fig.text(
            0.52,
            0.8,
            f"Resumo Total: Receitas R$ {total_income:.2f} | Gastos R$ {total_expense:.2f} | Saldo R$ {overall_balance:.2f}",
            ha="center",
            fontsize=14,
            fontweight="bold",
            bbox=dict(
                boxstyle="round,pad=0.6",
                facecolor=balance_color,
                alpha=0.2,
                edgecolor=balance_color,
                linewidth=1,
            ),
        )

        return self._fig_to_base64(fig)

    def generate_income_by_category(self):
        """Generate donut chart for income by category"""
        if not self.dataframes or self.dataframes["incomes"].empty:
            return None

        incomes_df = self.dataframes["incomes"]
        income_categories_df = self.dataframes["income_categories"]

        # Handle incomes without categories
        categorized_incomes = incomes_df[incomes_df["category_id"].notna()]
        uncategorized_incomes = incomes_df[incomes_df["category_id"].isna()]

        category_totals = pd.Series(dtype="float64")

        if not categorized_incomes.empty and not income_categories_df.empty:
            merged = categorized_incomes.merge(
                income_categories_df,
                left_on="category_id",
                right_on="id",
                suffixes=("", "_cat"),
            )
            category_totals = merged.groupby("name")["amount"].sum()

        if not uncategorized_incomes.empty:
            category_totals["Sem Categoria"] = uncategorized_incomes["amount"].sum()

        if category_totals.empty:
            return None

        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set2(range(len(category_totals)))

        # Create donut chart
        wedges, texts, autotexts = ax.pie(
            category_totals.values,
            labels=category_totals.index,
            autopct="%1.1f%%",
            colors=colors,
            startangle=90,
            pctdistance=0.75,
        )

        # Create donut hole
        centre_circle = plt.Circle((0, 0), 0.50, fc="white")
        ax.add_artist(centre_circle)

        ax.set_title("Receitas por Categoria", fontsize=16, fontweight="bold", pad=20)

        # Add value labels
        for i, (category, amount) in enumerate(category_totals.items()):
            autotexts[i].set_text(f"R$ {amount / 100:.0f}\n({autotexts[i].get_text()})")

        return self._fig_to_base64(fig)

    def generate_daily_spending_pattern(self):
        """Generate line chart showing daily spending pattern"""
        if not self.dataframes or self.dataframes["expenses"].empty:
            return None

        expenses_df = self.dataframes["expenses"].copy()
        expenses_df["spent_at"] = pd.to_datetime(expenses_df["spent_at"])

        # Extract only the date part (remove time)
        expenses_df["date_only"] = expenses_df["spent_at"].dt.date

        # Group by date only and sum amounts
        daily_totals = expenses_df.groupby("date_only")["amount"].sum()

        fig, ax = plt.subplots(figsize=(16, 8))

        # Convert dates back to datetime for plotting but keep only date part
        dates = pd.to_datetime(daily_totals.index)
        values = daily_totals.values / 100

        ax.plot(dates, values, marker="o", linewidth=2, markersize=6, alpha=0.8)
        ax.fill_between(dates, values, alpha=0.3)

        ax.set_title("Padrão de Gastos Diários", fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Data", fontsize=12)
        ax.set_ylabel("Valor (R$)", fontsize=12)
        ax.grid(True, alpha=0.3)

        # Format x-axis to show only dates
        import matplotlib.dates as mdates

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        # Ensure tight layout to prevent label cutoff
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def generate_financial_heatmap(self):
        """Generate heatmap showing financial activity"""
        if not self.dataframes:
            return None

        expenses_df = self.dataframes["expenses"].copy()
        incomes_df = self.dataframes["incomes"].copy()

        if expenses_df.empty and incomes_df.empty:
            return None

        # Prepare data for heatmap
        all_data = []

        if not expenses_df.empty:
            expenses_df["type"] = "Gastos"
            expenses_df["date"] = pd.to_datetime(expenses_df["spent_at"])
            all_data.append(expenses_df[["date", "amount", "type"]])

        if not incomes_df.empty:
            incomes_df["type"] = "Receitas"
            incomes_df["date"] = pd.to_datetime(incomes_df["received_at"])
            all_data.append(incomes_df[["date", "amount", "type"]])

        if not all_data:
            return None

        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df["weekday"] = combined_df["date"].dt.day_name()
        combined_df["week"] = combined_df["date"].dt.isocalendar().week

        # Create pivot table for heatmap
        heatmap_data = (
            combined_df.groupby(["week", "weekday", "type"])["amount"]
            .sum()
            .unstack(fill_value=0)
            / 100
        )

        if heatmap_data.empty:
            return None

        fig, ax = plt.subplots(figsize=(12, 8))

        # Create heatmap
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".2f",
            cmap="RdYlBu_r",
            ax=ax,
            cbar_kws={"label": "Valor (R$)"},
        )

        ax.set_title(
            "Mapa de Calor - Atividade Financeira por Semana",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("Tipo de Transação", fontsize=12)
        ax.set_ylabel("Semana do Ano", fontsize=12)

        return self._fig_to_base64(fig)


def generate_all_graphs(user):
    """Generate all graphs and return as dictionary"""
    generator = FinanceGraphGenerator(user)

    graphs = {
        "expense_category_graph": generator.generate_expenses_by_category(),
        "monthly_expenses_graph": generator.generate_monthly_expenses_trend(),
        "income_expenses_graph": generator.generate_income_vs_expenses(),
        "income_category_graph": generator.generate_income_by_category(),
        "daily_spending_graph": generator.generate_daily_spending_pattern(),
        "financial_heatmap_graph": generator.generate_financial_heatmap(),
    }

    return graphs


if __name__ == "__main__":
    print("🎨 Generating finance graphs...")
    graphs = generate_all_graphs()

    for graph_name, graph_data in graphs.items():
        status = "✅ Generated" if graph_data else "❌ No data"
        print(f"{graph_name}: {status}")
