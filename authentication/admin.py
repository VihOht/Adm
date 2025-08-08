from django.contrib import admin

from authentication.models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "created_at"]
    list_filter = ["username", "email"]
    search_fields = ["username", "email"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
