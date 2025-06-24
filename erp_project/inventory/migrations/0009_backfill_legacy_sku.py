from django.db import migrations


def backfill_legacy(apps, schema_editor):
    Product = apps.get_model('inventory', 'Product')
    for prod in Product.objects.exclude(sku=''):
        prod.legacy_sku = prod.sku
        prod.save(update_fields=['legacy_sku'])


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_sku_updates'),
    ]

    operations = [
        migrations.RunPython(backfill_legacy, reverse_code=migrations.RunPython.noop),
    ]
