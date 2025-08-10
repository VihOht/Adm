from django.contrib import admin

from .models import ExpenseCategory, Expenses, IncomeCategorys, Incomes

# Register your models here.


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color"]
    list_filter = ["user"]
    search_fields = ["name", "description"]
    ordering = ["user", "name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(IncomeCategorys)
class IncomeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "color"]
    list_filter = ["user"]
    search_fields = ["name", "description"]
    ordering = ["user", "name"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "category", "spent_at", "user"]
    list_filter = ["category", "spent_at", "user"]
    search_fields = ["description", "detailed_description"]
    date_hierarchy = "spent_at"
    ordering = ["-spent_at"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = ExpenseCategory.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Incomes)
class IncomesAdmin(admin.ModelAdmin):
    list_display = ["description", "amount", "category", "received_at", "user"]
    list_filter = ["category", "received_at", "user"]
    search_fields = ["description", "detailed_description"]
    date_hierarchy = "received_at"
    ordering = ["-received_at"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = IncomeCategorys.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
