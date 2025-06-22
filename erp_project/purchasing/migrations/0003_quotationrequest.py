from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('purchasing', '0002_payment'),
        ('accounts', '0006_add_profile_picture'),
        ('inventory', '0006_product_sale_price_product_vat_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50, unique=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.company')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='purchasing.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationRequestLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ean', models.CharField(blank=True, max_length=13)),
                ('serial_list', models.TextField(blank=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.product')),
                ('quotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='purchasing.quotationrequest')),
            ],
        ),
    ]
