# Generated by Django 5.2.3 on 2025-06-24 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_auto_company_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="letterhead",
            field=models.FileField(blank=True, null=True, upload_to="letterheads/"),
        ),
    ]
