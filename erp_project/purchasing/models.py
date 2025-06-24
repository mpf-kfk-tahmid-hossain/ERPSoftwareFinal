from decimal import Decimal
import random
from django.db import models
from django.utils import timezone
from accounts.models import Company
from inventory.models import Product, Warehouse, ProductSerial
from ledger.utils import post_entry


class Bank(models.Model):
    """Financial institution used for supplier payments."""

    name = models.CharField(max_length=100, unique=True)
    swift_code = models.CharField(max_length=11, unique=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Vendor providing products."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)

    trade_license_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    trn = models.CharField(max_length=15, blank=True, null=True, unique=True)
    vat_certificate = models.FileField(upload_to='vat_docs/', blank=True)

    iban = models.CharField(max_length=23, blank=True, null=True, unique=True)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, null=True, blank=True)

    address = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_connected = models.BooleanField(default=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class SupplierOTP(models.Model):
    """One-time passcode for supplier email verification."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """Return True if OTP is within 10 minutes and unused."""
        expiry = self.created_at + timezone.timedelta(minutes=10)
        return not self.is_used and timezone.now() < expiry


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
    acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

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
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f"Payment {self.amount}"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and self.status == self.STATUS_APPROVED:
            self.post_ledger_entry()

    def post_ledger_entry(self):
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


class PaymentApproval(models.Model):
    """Approval record for payments."""

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='approvals')
    approver = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    approved = models.BooleanField()
    comment = models.TextField(blank=True)
    approved_at = models.DateTimeField(auto_now_add=True)


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


class SupplierInvoice(models.Model):
    """Invoice from supplier linked to a PO."""

    number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='invoices/', blank=True)
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.number

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
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ean = models.CharField(max_length=13, blank=True)
    serial_list = models.TextField(blank=True)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

# Purchase Requisition models added by agent

class PurchaseRequisition(models.Model):
    """Request to procure a product."""

    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    number = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    specification = models.CharField(max_length=255, blank=True)
    justification = models.TextField(blank=True)
    items = models.JSONField(default=list, blank=True)
    requester = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.number


class PurchaseRequisitionApproval(models.Model):
    """Approval record for a requisition."""

    requisition = models.ForeignKey(
        PurchaseRequisition, on_delete=models.CASCADE, related_name='approvals'
    )
    approver = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    approved = models.BooleanField(null=True)
    comment = models.TextField(blank=True)
    level = models.PositiveIntegerField(default=1)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        state = 'Approved' if self.approved else 'Rejected'
        if self.approved is None:
            state = 'Pending'
        return f"{self.approver} - {state}"


class SupplierEvaluation(models.Model):
    """Store evaluation scores for suppliers."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='evaluations')
    score = models.DecimalField(max_digits=4, decimal_places=2)
    comments = models.TextField(blank=True)
    date = models.DateField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.supplier} {self.score}"
