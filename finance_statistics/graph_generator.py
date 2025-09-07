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
        """Generate stacked bar chart for expenses by category over time"""
        if not self.dataframes or self.dataframes["expenses"].empty:
            return None

        expenses_df = self.dataframes["expenses"]
        categories_df = self.dataframes["expense_categories"]

        # Merge expenses with categories
        merged = expenses_df.merge(
            categories_df, left_on="category_id", right_on="id", suffixes=("", "_cat")
        )

        # Add expenses without categories
        uncategorized = expenses_df[expenses_df["category_id"].isna()].copy()
        if not uncategorized.empty:
            uncategorized["name"] = "Sem categoria"
            uncategorized["color"] = "#9ca3af"
            merged = pd.concat([merged, uncategorized], ignore_index=True)

        if merged.empty:
            return None

        # Convert dates and create month-year periods
        merged["spent_at"] = pd.to_datetime(merged["spent_at"])
        merged["month_year"] = merged["spent_at"].dt.to_period("M")

        # Group by month and category
        monthly_category_data = (
            merged.groupby(["month_year", "name"])["amount"].sum().unstack(fill_value=0)
        )

        if monthly_category_data.empty:
            return None

        # Convert to reais
        monthly_category_data = monthly_category_data / 100

        fig, (ax, ax_legend) = plt.subplots(
            1, 2, figsize=(18, 10), gridspec_kw={"width_ratios": [3, 1]}
        )

        # Prepare data for stacked bar chart
        months = [str(month) for month in monthly_category_data.index]
        categories = monthly_category_data.columns

        # Create color map
        colors = plt.cm.Set3(range(len(categories)))
        category_colors = {}

        # Use predefined colors from database if available
        for i, category in enumerate(categories):
            if category != "Sem categoria":
                try:
                    cat_color = categories_df[categories_df["name"] == category][
                        "color"
                    ].iloc[0]
                    if cat_color and cat_color.startswith("#"):
                        category_colors[category] = cat_color
                    else:
                        category_colors[category] = colors[i]
                except:
                    category_colors[category] = colors[i]
            else:
                category_colors[category] = "#9ca3af"

        # Create stacked bars
        bottom = np.zeros(len(months))
        bars = []

        for category in categories:
            values = monthly_category_data[category].values
            color = category_colors[category]

            bar = ax.bar(
                months,
                values,
                bottom=bottom,
                label=category,
                color=color,
                alpha=0.8,
                edgecolor="white",
                linewidth=0.5,
            )
            bars.append(bar)
            bottom += values

        # Formatting
        ax.set_title(
            "Gastos por Categoria ao Longo do Tempo",
            fontsize=18,
            fontweight="bold",
            pad=30,
        )
        ax.set_xlabel("Mês/Ano", fontsize=14, fontweight="bold")
        ax.set_ylabel("Valor (R$)", fontsize=14, fontweight="bold")

        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Add grid
        ax.grid(True, alpha=0.3, axis="y", linestyle="-", linewidth=0.5)

        # Add total values on top of each bar
        monthly_totals = monthly_category_data.sum(axis=1)
        for i, (month, total) in enumerate(monthly_totals.items()):
            if total > 0:
                ax.text(
                    i,
                    total + total * 0.02,
                    f"R$ {total:.0f}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                )

        # Create detailed legend
        ax_legend.axis("off")
        ax_legend.text(
            0.05,
            0.95,
            "Análise de Gastos por Categoria",
            fontsize=14,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )

        # Calculate statistics for each category
        category_totals = monthly_category_data.sum(axis=0).sort_values(ascending=False)
        total_expenses = category_totals.sum()

        legend_info = []
        y_pos = 0.85

        # Add category breakdown
        for category, total in category_totals.items():
            percentage = (total / total_expenses) * 100 if total_expenses > 0 else 0
            avg_monthly = (
                total / len(monthly_category_data)
                if len(monthly_category_data) > 0
                else 0
            )

            # Color indicator
            ax_legend.add_patch(
                plt.Rectangle(
                    (0.05, y_pos - 0.015),
                    0.03,
                    0.025,
                    facecolor=category_colors[category],
                    transform=ax_legend.transAxes,
                )
            )

            # Category name and stats
            ax_legend.text(
                0.12,
                y_pos,
                f"{category}",
                fontsize=11,
                fontweight="bold",
                transform=ax_legend.transAxes,
            )
            ax_legend.text(
                0.12,
                y_pos - 0.025,
                f"Total: R$ {total:.2f} ({percentage:.1f}%)",
                fontsize=10,
                color="gray",
                transform=ax_legend.transAxes,
            )
            ax_legend.text(
                0.12,
                y_pos - 0.045,
                f"Média mensal: R$ {avg_monthly:.2f}",
                fontsize=9,
                color="darkgray",
                transform=ax_legend.transAxes,
            )

            y_pos -= 0.10

        # Add summary statistics
        y_pos -= 0.02
        ax_legend.text(
            0.05,
            y_pos,
            "📊 RESUMO GERAL",
            fontsize=12,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )
        y_pos -= 0.06

        summary_stats = [
            f"Total geral: R$ {total_expenses:.2f}",
            f"Categorias ativas: {len(category_totals[category_totals > 0])}",
            f"Período: {len(monthly_category_data)} meses",
            f"Média mensal: R$ {total_expenses / len(monthly_category_data):.2f}",
            f"Maior categoria: {category_totals.index[0]}",
            f"({(category_totals.iloc[0] / total_expenses * 100):.1f}% do total)",
        ]

        for stat in summary_stats:
            ax_legend.text(
                0.05,
                y_pos,
                stat,
                fontsize=10,
                color="black" if not stat.startswith("(") else "gray",
                transform=ax_legend.transAxes,
            )
            y_pos -= 0.04

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def generate_monthly_expenses_trend(self):
        """Generate line chart for monthly expenses trend"""
        if not self.dataframes or self.dataframes["expenses"].empty:
            return None

        expenses_df = self.dataframes["expenses"].copy()
        expenses_df["spent_at"] = pd.to_datetime(expenses_df["spent_at"])
        expenses_df["month_year"] = expenses_df["spent_at"].dt.to_period("M")

        monthly_totals = expenses_df.groupby("month_year")["amount"].sum()

        fig, (ax, ax_legend) = plt.subplots(
            1, 2, figsize=(16, 8), gridspec_kw={"width_ratios": [3, 1]}
        )

        x_labels = [str(period) for period in monthly_totals.index]
        y_values = monthly_totals.values / 100  # Convert to reais

        line = ax.plot(
            x_labels,
            y_values,
            marker="o",
            linewidth=3,
            markersize=8,
            color="#e74c3c",
            label="Gastos Mensais",
        )
        ax.fill_between(x_labels, y_values, alpha=0.3, color="#e74c3c")

        ax.set_title(
            "Tendência Mensal de Gastos", fontsize=16, fontweight="bold", pad=20
        )
        ax.set_xlabel("Mês/Ano", fontsize=12)
        ax.set_ylabel("Valor (R$)", fontsize=12)
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)

        # Create legend
        ax_legend.axis("off")
        ax_legend.text(
            0.05,
            0.95,
            "Estatísticas Mensais",
            fontsize=14,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )

        # Calculate statistics
        total_months = len(monthly_totals)
        avg_monthly = y_values.mean()
        max_month = monthly_totals.idxmax()
        max_value = y_values.max()
        min_month = monthly_totals.idxmin()
        min_value = y_values.min()
        trend = (
            "Crescente"
            if y_values[-1] > y_values[0]
            else "Decrescente"
            if y_values[-1] < y_values[0]
            else "Estável"
        )

        legend_info = [
            f"Período analisado: {total_months} meses",
            f"Média mensal: R$ {avg_monthly:.2f}",
            f"Maior gasto: R$ {max_value:.2f}",
            f"({max_month})",
            f"Menor gasto: R$ {min_value:.2f}",
            f"({min_month})",
            f"Tendência: {trend}",
            f"Total acumulado: R$ {y_values.sum():.2f}",
        ]

        y_pos = 0.85
        for info in legend_info:
            color = "black" if not info.startswith("(") else "gray"
            fontweight = "bold" if not info.startswith("(") else "normal"
            ax_legend.text(
                0.05,
                y_pos,
                info,
                fontsize=10,
                color=color,
                fontweight=fontweight,
                transform=ax_legend.transAxes,
            )
            y_pos -= 0.08

        plt.tight_layout()
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

        # Create figure with legend space
        fig, (ax, ax_legend) = plt.subplots(
            1, 2, figsize=(18, 10), gridspec_kw={"width_ratios": [3, 1]}
        )

        # Prepare data for grouped bar chart
        months = [str(month) for month in all_months]
        x_pos = range(len(months))
        width = 0.35

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

        # Add value labels on bars
        for bars, values in [
            (income_bars, monthly_incomes.values),
            (expense_bars, monthly_expenses.values),
        ]:
            for bar, value in zip(bars, values):
                if value > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2.0,
                        value + max_value * 0.02,
                        f"R$ {value:.0f}",
                        ha="center",
                        va="bottom",
                        fontsize=9,
                        fontweight="bold",
                    )

        # Calculate monthly balance and add balance line
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
        y_max = max_value * 1.25
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

        ax.legend(
            loc="upper left", frameon=True, fancybox=True, shadow=True, fontsize=12
        )
        ax.grid(True, alpha=0.3, axis="y", linestyle="-", linewidth=0.5)

        # Create detailed legend
        ax_legend.axis("off")
        ax_legend.text(
            0.05,
            0.95,
            "Resumo Financeiro",
            fontsize=14,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )

        # Calculate statistics
        total_income = monthly_incomes.sum()
        total_expense = monthly_expenses.sum()
        overall_balance = total_income - total_expense
        avg_income = monthly_incomes.mean()
        avg_expense = monthly_expenses.mean()
        avg_balance = monthly_balance.mean()

        positive_months = (monthly_balance > 0).sum()
        negative_months = (monthly_balance < 0).sum()

        best_month = monthly_balance.idxmax()
        best_balance = monthly_balance.max()
        worst_month = monthly_balance.idxmin()
        worst_balance = monthly_balance.min()

        legend_info = [
            ("💰 RECEITAS", "#10b981"),
            (f"Total: R$ {total_income:.2f}", "black"),
            (f"Média mensal: R$ {avg_income:.2f}", "gray"),
            ("", ""),
            ("💸 GASTOS", "#ef4444"),
            (f"Total: R$ {total_expense:.2f}", "black"),
            (f"Média mensal: R$ {avg_expense:.2f}", "gray"),
            ("", ""),
            ("📊 SALDO", "#6366f1"),
            (f"Saldo total: R$ {overall_balance:.2f}", "black"),
            (f"Saldo médio: R$ {avg_balance:.2f}", "gray"),
            ("", ""),
            ("📈 ANÁLISE", "black"),
            (f"Meses positivos: {positive_months}", "green"),
            (
                f"Meses negativos: {negative_months}",
                "red" if negative_months > 0 else "gray",
            ),
            ("", ""),
            (f"Melhor mês: {best_month}", "green"),
            (f"R$ {best_balance:.2f}", "gray"),
            (f"Pior mês: {worst_month}", "red"),
            (f"R$ {worst_balance:.2f}", "gray"),
        ]

        y_pos = 0.85
        for info, color in legend_info:
            if info == "":
                y_pos -= 0.02
                continue
            fontweight = (
                "bold" if info.startswith(("💰", "💸", "📊", "📈")) else "normal"
            )
            fontsize = 11 if fontweight == "bold" else 10
            ax_legend.text(
                0.05,
                y_pos,
                info,
                fontsize=fontsize,
                color=color,
                fontweight=fontweight,
                transform=ax_legend.transAxes,
            )
            y_pos -= 0.05

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def generate_income_by_category(self):
        """Generate stacked bar chart for income by category over time"""
        if not self.dataframes or self.dataframes["incomes"].empty:
            return None

        incomes_df = self.dataframes["incomes"]
        income_categories_df = self.dataframes["income_categories"]

        # Merge incomes with categories
        merged = incomes_df.merge(
            income_categories_df,
            left_on="category_id",
            right_on="id",
            suffixes=("", "_cat"),
        )

        # Add incomes without categories
        uncategorized = incomes_df[incomes_df["category_id"].isna()].copy()
        if not uncategorized.empty:
            uncategorized["name"] = "Sem categoria"
            uncategorized["color"] = "#9ca3af"
            merged = pd.concat([merged, uncategorized], ignore_index=True)

        if merged.empty:
            return None

        # Convert dates and create month-year periods
        merged["received_at"] = pd.to_datetime(merged["received_at"])
        merged["month_year"] = merged["received_at"].dt.to_period("M")

        # Group by month and category
        monthly_category_data = (
            merged.groupby(["month_year", "name"])["amount"].sum().unstack(fill_value=0)
        )

        if monthly_category_data.empty:
            return None

        # Convert to reais
        monthly_category_data = monthly_category_data / 100

        fig, (ax, ax_legend) = plt.subplots(
            1, 2, figsize=(18, 10), gridspec_kw={"width_ratios": [3, 1]}
        )

        # Prepare data for stacked bar chart
        months = [str(month) for month in monthly_category_data.index]
        categories = monthly_category_data.columns

        # Create color map
        colors = plt.cm.Set2(range(len(categories)))
        category_colors = {}

        # Use predefined colors from database if available
        for i, category in enumerate(categories):
            if category != "Sem categoria":
                try:
                    cat_color = income_categories_df[
                        income_categories_df["name"] == category
                    ]["color"].iloc[0]
                    if cat_color and cat_color.startswith("#"):
                        category_colors[category] = cat_color
                    else:
                        category_colors[category] = colors[i]
                except:
                    category_colors[category] = colors[i]
            else:
                category_colors[category] = "#9ca3af"

        # Create stacked bars
        bottom = np.zeros(len(months))
        bars = []

        for category in categories:
            values = monthly_category_data[category].values
            color = category_colors[category]

            bar = ax.bar(
                months,
                values,
                bottom=bottom,
                label=category,
                color=color,
                alpha=0.8,
                edgecolor="white",
                linewidth=0.5,
            )
            bars.append(bar)
            bottom += values

        # Formatting
        ax.set_title(
            "Receitas por Categoria ao Longo do Tempo",
            fontsize=18,
            fontweight="bold",
            pad=30,
        )
        ax.set_xlabel("Mês/Ano", fontsize=14, fontweight="bold")
        ax.set_ylabel("Valor (R$)", fontsize=14, fontweight="bold")

        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Add grid
        ax.grid(True, alpha=0.3, axis="y", linestyle="-", linewidth=0.5)

        # Add total values on top of each bar
        monthly_totals = monthly_category_data.sum(axis=1)
        for i, (month, total) in enumerate(monthly_totals.items()):
            if total > 0:
                ax.text(
                    i,
                    total + total * 0.02,
                    f"R$ {total:.0f}",
                    ha="center",
                    va="bottom",
                    fontweight="bold",
                    fontsize=10,
                )

        # Create detailed legend
        ax_legend.axis("off")
        ax_legend.text(
            0.05,
            0.95,
            "Análise de Receitas por Categoria",
            fontsize=14,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )

        # Calculate statistics for each category
        category_totals = monthly_category_data.sum(axis=0).sort_values(ascending=False)
        total_incomes = category_totals.sum()

        legend_info = []
        y_pos = 0.85

        # Add category breakdown
        for category, total in category_totals.items():
            percentage = (total / total_incomes) * 100 if total_incomes > 0 else 0
            avg_monthly = (
                total / len(monthly_category_data)
                if len(monthly_category_data) > 0
                else 0
            )

            # Color indicator
            ax_legend.add_patch(
                plt.Rectangle(
                    (0.05, y_pos - 0.015),
                    0.03,
                    0.025,
                    facecolor=category_colors[category],
                    transform=ax_legend.transAxes,
                )
            )

            # Category name and stats
            ax_legend.text(
                0.12,
                y_pos,
                f"{category}",
                fontsize=11,
                fontweight="bold",
                transform=ax_legend.transAxes,
            )
            ax_legend.text(
                0.12,
                y_pos - 0.025,
                f"Total: R$ {total:.2f} ({percentage:.1f}%)",
                fontsize=10,
                color="gray",
                transform=ax_legend.transAxes,
            )
            ax_legend.text(
                0.12,
                y_pos - 0.045,
                f"Média mensal: R$ {avg_monthly:.2f}",
                fontsize=9,
                color="darkgray",
                transform=ax_legend.transAxes,
            )

            y_pos -= 0.10

        # Add summary statistics
        y_pos -= 0.02
        ax_legend.text(
            0.05,
            y_pos,
            "📊 RESUMO GERAL",
            fontsize=12,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )
        y_pos -= 0.06

        summary_stats = [
            f"Total geral: R$ {total_incomes:.2f}",
            f"Categorias ativas: {len(category_totals[category_totals > 0])}",
            f"Período: {len(monthly_category_data)} meses",
            f"Média mensal: R$ {total_incomes / len(monthly_category_data):.2f}",
            f"Maior categoria: {category_totals.index[0]}",
            f"({(category_totals.iloc[0] / total_incomes * 100):.1f}% do total)",
        ]

        for stat in summary_stats:
            ax_legend.text(
                0.05,
                y_pos,
                stat,
                fontsize=10,
                color="black" if not stat.startswith("(") else "gray",
                transform=ax_legend.transAxes,
            )
            y_pos -= 0.04

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def generate_daily_spending_pattern(self):
        """Generate line chart showing daily spending pattern"""
        if not self.dataframes or self.dataframes["expenses"].empty:
            return None

        expenses_df = self.dataframes["expenses"].copy()
        expenses_df["spent_at"] = pd.to_datetime(expenses_df["spent_at"])
        expenses_df["date_only"] = expenses_df["spent_at"].dt.date

        daily_totals = expenses_df.groupby("date_only")["amount"].sum()

        fig, (ax, ax_legend) = plt.subplots(
            1, 2, figsize=(18, 8), gridspec_kw={"width_ratios": [3, 1]}
        )

        dates = pd.to_datetime(daily_totals.index)
        values = daily_totals.values / 100

        ax.plot(
            dates,
            values,
            marker="o",
            linewidth=2,
            markersize=6,
            alpha=0.8,
            color="#e74c3c",
            label="Gastos Diários",
        )
        ax.fill_between(dates, values, alpha=0.3, color="#e74c3c")

        ax.set_title("Padrão de Gastos Diários", fontsize=16, fontweight="bold", pad=20)
        ax.set_xlabel("Data", fontsize=12)
        ax.set_ylabel("Valor (R$)", fontsize=12)
        ax.grid(True, alpha=0.3)

        import matplotlib.dates as mdates

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))

        # Adjust date locator based on data range
        date_range = (dates.max() - dates.min()).days
        if date_range <= 30:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        elif date_range <= 90:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        else:
            ax.xaxis.set_major_locator(mdates.MonthLocator())

        plt.xticks(rotation=45)

        # Create legend with statistics
        ax_legend.axis("off")
        ax_legend.text(
            0.05,
            0.95,
            "Estatísticas Diárias",
            fontsize=14,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )

        # Calculate statistics
        total_days = len(daily_totals)
        total_amount = values.sum()
        avg_daily = values.mean()
        max_day = daily_totals.idxmax()
        max_value = values.max()
        min_day = daily_totals.idxmin()
        min_value = values.min()

        # Weekday analysis
        expenses_df["weekday"] = expenses_df["spent_at"].dt.day_name()
        weekday_avg = expenses_df.groupby("weekday")["amount"].mean() / 100
        highest_weekday = weekday_avg.idxmax()
        lowest_weekday = weekday_avg.idxmin()

        legend_info = [
            f"Período: {total_days} dias",
            f"Total gasto: R$ {total_amount:.2f}",
            f"Média diária: R$ {avg_daily:.2f}",
            "",
            f"Maior gasto: R$ {max_value:.2f}",
            f"({max_day.strftime('%d/%m/%Y')})",
            f"Menor gasto: R$ {min_value:.2f}",
            f"({min_day.strftime('%d/%m/%Y')})",
            "",
            "📅 Análise por dia da semana:",
            f"Dia com mais gastos: {highest_weekday}",
            f"R$ {weekday_avg[highest_weekday]:.2f} (média)",
            f"Dia com menos gastos: {lowest_weekday}",
            f"R$ {weekday_avg[lowest_weekday]:.2f} (média)",
        ]

        y_pos = 0.85
        for info in legend_info:
            if info == "":
                y_pos -= 0.03
                continue
            color = "black" if not info.startswith("(") else "gray"
            fontweight = "bold" if info.startswith("📅") else "normal"
            fontsize = 11 if fontweight == "bold" else 10
            ax_legend.text(
                0.05,
                y_pos,
                info,
                fontsize=fontsize,
                color=color,
                fontweight=fontweight,
                transform=ax_legend.transAxes,
            )
            y_pos -= 0.06

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

        fig, (ax, ax_legend) = plt.subplots(
            1, 2, figsize=(16, 10), gridspec_kw={"width_ratios": [3, 1]}
        )

        # Create heatmap
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".0f",
            cmap="RdYlBu_r",
            ax=ax,
            cbar_kws={"label": "Valor (R$)"},
            linewidths=0.5,
        )

        ax.set_title(
            "Mapa de Calor - Atividade Financeira por Semana",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )
        ax.set_xlabel("Tipo de Transação", fontsize=12)
        ax.set_ylabel("Semana do Ano", fontsize=12)

        # Create legend with analysis
        ax_legend.axis("off")
        ax_legend.text(
            0.05,
            0.95,
            "Análise do Mapa de Calor",
            fontsize=14,
            fontweight="bold",
            transform=ax_legend.transAxes,
        )

        # Calculate statistics for legend
        weeks_analyzed = len(heatmap_data.index)

        if "Gastos" in heatmap_data.columns:
            total_expenses = heatmap_data["Gastos"].sum()
            avg_weekly_expenses = heatmap_data["Gastos"].mean()
            max_expense_week = heatmap_data["Gastos"].idxmax()
        else:
            total_expenses = avg_weekly_expenses = max_expense_week = 0

        if "Receitas" in heatmap_data.columns:
            total_incomes = heatmap_data["Receitas"].sum()
            avg_weekly_incomes = heatmap_data["Receitas"].mean()
            max_income_week = heatmap_data["Receitas"].idxmax()
        else:
            total_incomes = avg_weekly_incomes = max_income_week = 0

        legend_info = [
            f"📊 Semanas analisadas: {weeks_analyzed}",
            "",
            "💸 GASTOS SEMANAIS:",
            f"Total: R$ {total_expenses:.2f}",
            f"Média: R$ {avg_weekly_expenses:.2f}",
            f"Pico: Semana {max_expense_week}" if max_expense_week else "Sem dados",
            "",
            "💰 RECEITAS SEMANAIS:",
            f"Total: R$ {total_incomes:.2f}",
            f"Média: R$ {avg_weekly_incomes:.2f}",
            f"Pico: Semana {max_income_week}" if max_income_week else "Sem dados",
            "",
            "🎯 INTERPRETAÇÃO:",
            "• Cores mais quentes = maior atividade",
            "• Cores mais frias = menor atividade",
            "• Branco = sem movimentação",
            "",
            "📈 PADRÕES:",
            "• Identifique semanas com alta atividade",
            "• Compare receitas vs gastos por período",
            "• Visualize tendências temporais",
        ]

        y_pos = 0.85
        for info in legend_info:
            if info == "":
                y_pos -= 0.025
                continue
            color = "black"
            fontweight = "normal"
            fontsize = 10

            if info.startswith(("📊", "💸", "💰", "🎯", "📈")):
                fontweight = "bold"
                fontsize = 11
            elif info.startswith("•"):
                color = "gray"
                fontsize = 9

            ax_legend.text(
                0.05,
                y_pos,
                info,
                fontsize=fontsize,
                color=color,
                fontweight=fontweight,
                transform=ax_legend.transAxes,
            )
            y_pos -= 0.04

        plt.tight_layout()
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
