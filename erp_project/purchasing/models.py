from decimal import Decimal
from django.db import models
from accounts.models import Company
from inventory.models import Product, Warehouse, ProductSerial
from ledger.utils import post_entry


class Supplier(models.Model):
    """Vendor providing products."""
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    """Simple purchase order."""
    DRAFT = 'draft'
    SUBMITTED = 'submitted'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (SUBMITTED, 'Submitted'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.order_number


class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class Payment(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    METHOD_CASH = 'cash'
    METHOD_BANK = 'bank'
    METHOD_CHOICES = [
        (METHOD_CASH, 'Cash'),
        (METHOD_BANK, 'Bank'),
    ]
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    is_advance = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount}"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating:
            if self.is_advance:
                debit = 'Supplier Advance'
                credit = 'Cash' if self.method == self.METHOD_CASH else 'Bank'
            else:
                debit = 'Supplier'
                if Payment.objects.filter(
                    purchase_order=self.purchase_order, is_advance=True
                ).exists():
                    credit = 'Supplier Advance'
                else:
                    credit = 'Cash' if self.method == self.METHOD_CASH else 'Bank'
            post_entry(
                self.company,
                'Payment',
                [
                    (debit, self.amount, 0),
                    (credit, 0, self.amount),
                ],
            )


class GoodsReceipt(models.Model):
    """Record incoming goods against a PO."""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty_received = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    ean = models.CharField(max_length=13)
    serial = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"GRN {self.purchase_order.order_number} {self.product}"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating:
            if self.product.track_serial:
                ProductSerial.objects.create(product=self.product, serial=self.serial)
            amount = Decimal(self.qty_received) * self.product.sale_price
            post_entry(
                self.purchase_order.company,
                f"GRN {self.purchase_order.order_number}",
                [
                    ("Inventory", amount, 0),
                    ("Supplier", 0, amount),
                ],
            )


class QuotationRequest(models.Model):
    """Request quotation from a supplier for specific products."""

    number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    date = models.DateField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.number


class QuotationRequestLine(models.Model):
    quotation = models.ForeignKey(
        QuotationRequest, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    ean = models.CharField(max_length=13, blank=True)
    serial_list = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product} x {self.quantity}"
