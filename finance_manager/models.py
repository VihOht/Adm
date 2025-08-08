from colorfield.fields import ColorField
from django.conf import settings
from django.db import models

# Create your models here.


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    color = ColorField(default="#FFFFFF")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Expense Categories"


class Expenses(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    spent_at = models.DateField()
    description = models.CharField(max_length=100)
    detailed_description = models.CharField(max_length=600)
    amount = models.IntegerField()


class IncomeCategorys(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    color = ColorField(default="#FFFFFF")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Income Categories"


class Incomes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(
        IncomeCategorys, on_delete=models.CASCADE, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateField()
    description = models.CharField(max_length=100)
    detailed_description = models.CharField(max_length=600)
    amount = models.IntegerField()
