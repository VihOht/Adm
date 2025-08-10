# Generated manually for adding user field to categories

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("finance_manager", "0006_rename_spent_at_incomes_received_at_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="expensecategory",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="incomecategorys",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="expensecategory",
            unique_together={("user", "name")},
        ),
        migrations.AlterUniqueTogether(
            name="incomecategorys",
            unique_together={("user", "name")},
        ),
    ]
