from django.db import migrations


def migrate_skus(apps, schema_editor):
    Product = apps.get_model('inventory', 'Product')
    ProductCategory = apps.get_model('inventory', 'ProductCategory')
    Company = apps.get_model('accounts', 'Company')

    groups = {}
    for product in Product.objects.all().order_by('id'):
        company = product.company
        category = product.category
        cat_code = category.code if category else 'GEN'
        key = (company.id, category.id if category else None)
        seq = groups.get(key, 0) + 1
        groups[key] = seq
        if product.sku:
            product.legacy_sku = product.sku
        product.sku = f"{company.code}-{cat_code}-{seq:06d}"
        product.save(update_fields=['sku', 'legacy_sku'])


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_backfill_legacy_sku'),
    ]

    operations = [
        migrations.RunPython(migrate_skus, reverse_code=migrations.RunPython.noop),
    ]
