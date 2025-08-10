"""
Management command to import/export financial data from/to JSON files.
"""

import json
import os
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from finance_manager.models import ExpenseCategory, Expenses, IncomeCategorys, Incomes

User = get_user_model()


class Command(BaseCommand):
    help = "Import or export financial data from/to JSON files"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["import", "export"],
            help="Action to perform: import or export",
        )
        parser.add_argument(
            "--file",
            type=str,
            required=True,
            help="Path to the JSON file",
        )
        parser.add_argument(
            "--user",
            type=str,
            help="Username for import/export (required for import, optional for export)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before import",
        )

    def handle(self, *args, **options):
        action = options["action"]
        file_path = options["file"]
        username = options["user"]
        clear_data = options.get("clear", False)

        if action == "import":
            if not username:
                raise CommandError("Username is required for import action")
            self.import_data(file_path, username, clear_data)
        elif action == "export":
            self.export_data(file_path, username)

    def import_data(self, file_path, username, clear_data):
        """Import financial data from JSON file"""
        if not os.path.exists(file_path):
            raise CommandError(f"File {file_path} does not exist")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON file: {e}")

        self.stdout.write(f"Importing data for user: {username}")

        with transaction.atomic():
            if clear_data:
                self.stdout.write("Clearing existing data...")
                Expenses.objects.filter(user=user).delete()
                Incomes.objects.filter(user=user).delete()
                ExpenseCategory.objects.filter(user=user).delete()
                IncomeCategorys.objects.filter(user=user).delete()

            # Import expense categories
            expense_categories = {}
            for cat_data in data.get("expense_categories", []):
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
                    self.stdout.write(f"Created expense category: {category.name}")

            # Import income categories
            income_categories = {}
            for cat_data in data.get("income_categories", []):
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
                    self.stdout.write(f"Created income category: {category.name}")

            # Import expenses
            expenses_created = 0
            for expense_data in data.get("expenses", []):
                category = None
                if expense_data.get("category"):
                    category = expense_categories.get(expense_data["category"])

                try:
                    spent_at = datetime.strptime(
                        expense_data["spent_at"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    self.stdout.write(
                        f"Invalid date format for expense: {expense_data.get('spent_at', 'N/A')}"
                    )
                    continue

                Expenses.objects.create(
                    user=user,
                    category=category,
                    spent_at=spent_at,
                    description=expense_data.get("description", ""),
                    detailed_description=expense_data.get("detailed_description", ""),
                    amount=int(expense_data.get("amount", 0)),
                )
                expenses_created += 1

            # Import incomes
            incomes_created = 0
            for income_data in data.get("incomes", []):
                category = None
                if income_data.get("category"):
                    category = income_categories.get(income_data["category"])

                try:
                    received_at = datetime.strptime(
                        income_data["received_at"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    self.stdout.write(
                        f"Invalid date format for income: {income_data.get('received_at', 'N/A')}"
                    )
                    continue

                Incomes.objects.create(
                    user=user,
                    category=category,
                    received_at=received_at,
                    description=income_data.get("description", ""),
                    detailed_description=income_data.get("detailed_description", ""),
                    amount=int(income_data.get("amount", 0)),
                )
                incomes_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported:\n"
                f"- {len(expense_categories)} expense categories\n"
                f"- {len(income_categories)} income categories\n"
                f"- {expenses_created} expenses\n"
                f"- {incomes_created} incomes"
            )
        )

    def export_data(self, file_path, username=None):
        """Export financial data to JSON file"""
        if username:
            try:
                user = User.objects.get(username=username)
                users = [user]
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' does not exist")
        else:
            users = User.objects.all()

        data = {
            "exported_at": datetime.now().isoformat(),
            "users": [],
        }

        for user in users:
            user_data = {
                "username": user.username,
                "expense_categories": [],
                "income_categories": [],
                "expenses": [],
                "incomes": [],
            }

            # Export expense categories
            for category in ExpenseCategory.objects.filter(user=user):
                user_data["expense_categories"].append(
                    {
                        "name": category.name,
                        "description": category.description,
                        "color": category.color,
                    }
                )

            # Export income categories
            for category in IncomeCategorys.objects.filter(user=user):
                user_data["income_categories"].append(
                    {
                        "name": category.name,
                        "description": category.description,
                        "color": category.color,
                    }
                )

            # Export expenses
            for expense in Expenses.objects.filter(user=user).order_by("-spent_at"):
                user_data["expenses"].append(
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
                user_data["incomes"].append(
                    {
                        "category": income.category.name if income.category else None,
                        "received_at": income.received_at.strftime("%Y-%m-%d"),
                        "description": income.description,
                        "detailed_description": income.detailed_description,
                        "amount": income.amount,
                        "created_at": income.created_at.isoformat(),
                    }
                )

            data["users"].append(user_data)

        # If exporting for a single user, flatten the structure
        if username and len(data["users"]) == 1:
            user_data = data["users"][0]
            data = {
                "exported_at": data["exported_at"],
                "username": user_data["username"],
                "expense_categories": user_data["expense_categories"],
                "income_categories": user_data["income_categories"],
                "expenses": user_data["expenses"],
                "incomes": user_data["incomes"],
            }

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except IOError as e:
            raise CommandError(f"Error writing to file: {e}")

        total_records = 0
        if username:
            user_data = data
            total_records = (
                len(user_data["expense_categories"])
                + len(user_data["income_categories"])
                + len(user_data["expenses"])
                + len(user_data["incomes"])
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully exported data for user '{username}':\n"
                    f"- {len(user_data['expense_categories'])} expense categories\n"
                    f"- {len(user_data['income_categories'])} income categories\n"
                    f"- {len(user_data['expenses'])} expenses\n"
                    f"- {len(user_data['incomes'])} incomes\n"
                    f"Total records: {total_records}"
                )
            )
        else:
            total_users = len(data["users"])
            for user_data in data["users"]:
                total_records += (
                    len(user_data["expense_categories"])
                    + len(user_data["income_categories"])
                    + len(user_data["expenses"])
                    + len(user_data["incomes"])
                )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully exported data for {total_users} users\n"
                    f"Total records: {total_records}"
                )
            )

        self.stdout.write(f"Data exported to: {file_path}")
