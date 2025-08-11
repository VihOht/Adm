import calendar
from collections import defaultdict

import pandas as pd
from django.utils import timezone

from finance_statistics.utils import get_finance_dataframes


class TransactionCalendarGenerator:
    def __init__(self, user):
        self.user = user
        self.dataframes = get_finance_dataframes(user)

    def generate_calendar_data(self, year=None, month=None):
        """Generate calendar data for transactions"""
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        # Prepare transaction data
        calendar_data = self._prepare_transaction_data(year, month)

        # Generate calendar structure
        cal = calendar.monthcalendar(year, month)

        # Create calendar with transaction data
        calendar_with_data = []
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append(
                        {
                            "day": 0,
                            "is_empty": True,
                            "total_amount": 0,
                            "transaction_count": 0,
                            "expenses": 0,
                            "incomes": 0,
                            "balance": 0,
                            "transactions": [],
                        }
                    )
                else:
                    day_key = f"{year}-{month:02d}-{day:02d}"
                    day_data = calendar_data.get(
                        day_key,
                        {
                            "total_amount": 0,
                            "transaction_count": 0,
                            "expenses": 0,
                            "incomes": 0,
                            "balance": 0,
                            "transactions": [],
                        },
                    )

                    week_data.append(
                        {"day": day, "date": day_key, "is_empty": False, **day_data}
                    )
            calendar_with_data.append(week_data)

        return {
            "calendar": calendar_with_data,
            "month_name": calendar.month_name[month],
            "year": year,
            "month": month,
            "statistics": self._get_month_statistics(calendar_data),
        }

    def _prepare_transaction_data(self, year, month):
        """Prepare transaction data grouped by day"""
        calendar_data = defaultdict(
            lambda: {
                "total_amount": 0,
                "transaction_count": 0,
                "expenses": 0,
                "incomes": 0,
                "balance": 0,
                "transactions": [],
            }
        )

        # Process expenses
        if not self.dataframes["expenses"].empty:
            expenses_df = self.dataframes["expenses"].copy()
            expenses_df["spent_at"] = pd.to_datetime(expenses_df["spent_at"])

            # Filter by year and month
            month_expenses = expenses_df[
                (expenses_df["spent_at"].dt.year == year)
                & (expenses_df["spent_at"].dt.month == month)
            ]

            # Get categories for expenses
            categories_df = self.dataframes["expense_categories"]

            for _, expense in month_expenses.iterrows():
                day_key = expense["spent_at"].strftime("%Y-%m-%d")
                amount = expense["amount"] / 100  # Convert to reais

                # Get category name
                category_name = "Sem Categoria"
                if not categories_df.empty and pd.notna(expense["category_id"]):
                    category_row = categories_df[
                        categories_df["id"] == expense["category_id"]
                    ]
                    if not category_row.empty:
                        category_name = category_row.iloc[0]["name"]

                calendar_data[day_key]["expenses"] += amount
                calendar_data[day_key]["total_amount"] += amount
                calendar_data[day_key]["transaction_count"] += 1
                calendar_data[day_key]["transactions"].append(
                    {
                        "type": "expense",
                        "amount": amount,
                        "description": expense.get("description", "Sem descrição"),
                        "category": category_name,
                        "time": expense["spent_at"].strftime("%H:%M"),
                        "id": expense["id"],
                    }
                )

        # Process incomes
        if not self.dataframes["incomes"].empty:
            incomes_df = self.dataframes["incomes"].copy()
            incomes_df["received_at"] = pd.to_datetime(incomes_df["received_at"])

            # Filter by year and month
            month_incomes = incomes_df[
                (incomes_df["received_at"].dt.year == year)
                & (incomes_df["received_at"].dt.month == month)
            ]

            # Get categories for incomes
            income_categories_df = self.dataframes["income_categories"]

            for _, income in month_incomes.iterrows():
                day_key = income["received_at"].strftime("%Y-%m-%d")
                amount = income["amount"] / 100  # Convert to reais

                # Get category name
                category_name = "Sem Categoria"
                if not income_categories_df.empty and pd.notna(income["category_id"]):
                    category_row = income_categories_df[
                        income_categories_df["id"] == income["category_id"]
                    ]
                    if not category_row.empty:
                        category_name = category_row.iloc[0]["name"]

                calendar_data[day_key]["incomes"] += amount
                calendar_data[day_key]["total_amount"] += amount
                calendar_data[day_key]["transaction_count"] += 1
                calendar_data[day_key]["transactions"].append(
                    {
                        "type": "income",
                        "amount": amount,
                        "description": income.get("description", "Sem descrição"),
                        "category": category_name,
                        "time": income["received_at"].strftime("%H:%M"),
                        "id": income["id"],
                    }
                )

        # Calculate balance for each day
        for day_data in calendar_data.values():
            day_data["balance"] = day_data["incomes"] - day_data["expenses"]
            # Sort transactions by time
            day_data["transactions"].sort(key=lambda x: x["time"])

        return dict(calendar_data)

    def _get_month_statistics(self, calendar_data):
        """Get month-level statistics"""
        total_expenses = sum(day["expenses"] for day in calendar_data.values())
        total_incomes = sum(day["incomes"] for day in calendar_data.values())
        total_transactions = sum(
            day["transaction_count"] for day in calendar_data.values()
        )

        days_with_expenses = sum(
            1 for day in calendar_data.values() if day["expenses"] > 0
        )
        days_with_incomes = sum(
            1 for day in calendar_data.values() if day["incomes"] > 0
        )
        days_with_activity = sum(
            1 for day in calendar_data.values() if day["transaction_count"] > 0
        )

        avg_daily_expenses = total_expenses / max(days_with_expenses, 1)
        avg_daily_incomes = total_incomes / max(days_with_incomes, 1)

        return {
            "total_expenses": total_expenses,
            "total_incomes": total_incomes,
            "total_balance": total_incomes - total_expenses,
            "total_transactions": total_transactions,
            "days_with_activity": days_with_activity,
            "days_with_expenses": days_with_expenses,
            "days_with_incomes": days_with_incomes,
            "avg_daily_expenses": avg_daily_expenses,
            "avg_daily_incomes": avg_daily_incomes,
        }
