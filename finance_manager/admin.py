from django.contrib import admin

from .models import ExpenseCategory, Expenses

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
