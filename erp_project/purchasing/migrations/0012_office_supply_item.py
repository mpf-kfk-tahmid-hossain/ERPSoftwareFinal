from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0008_add_letterhead_field"),
        ("inventory", "0010_migrate_skus"),
        ("purchasing", "0011_add_service_item"),
    ]

    operations = [
        migrations.CreateModel(
            name="OfficeSupplyItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "company",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="accounts.company"),
                ),
                (
                    "unit",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="inventory.productunit"),
                ),
            ],
            options={"unique_together": {("name", "company")}},
        ),
    ]
