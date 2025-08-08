from django.contrib import admin

from .models import ExpenseCategory, Expenses, Incomes

# Register your models here.


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "category", "spent_at", "user"]
    list_filter = ["category", "spent_at", "user"]
    search_fields = ["description", "detailed_description"]
    date_hierarchy = "spent_at"
    ordering = ["-spent_at"]


@admin.register(Incomes)
class IncomesAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "category", "received_at", "user"]
    list_filter = ["category", "received_at", "user"]
    search_fields = ["description", "detailed_description"]
    date_hierarchy = "received_at"
    ordering = ["-received_at"]
