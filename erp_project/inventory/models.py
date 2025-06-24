from django.db import models
from accounts.models import Company


class Warehouse(models.Model):
    """Storage location for inventory."""

    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class ProductCategory(models.Model):
    """Hierarchical grouping for products."""

    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_discontinued = models.BooleanField(default=False)
    required_identifiers = models.ManyToManyField('IdentifierType', blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "company"],
                name="unique_category_per_company",
            )
        ]

    def is_ancestor_of(self, other: 'ProductCategory') -> bool:
        """Return True if this category is an ancestor of ``other``."""
        current = other.parent
        while current:
            if current.pk == self.pk:
                return True
            current = current.parent
        return False

    @property
    def full_path(self) -> str:
        """Return the full path name using ``>`` as separator."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name


class ProductUnit(models.Model):
    """Unit of measure for a product."""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Product master record."""
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True)
    unit = models.ForeignKey(ProductUnit, on_delete=models.PROTECT)
    brand = models.CharField(max_length=255, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    is_discontinued = models.BooleanField(default=False)
    track_serial = models.BooleanField(default=False)
    vat_rate = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    specs = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    """Photo attached to a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_photos/')


class StockLot(models.Model):
    """Physical batch of product in a warehouse."""
    batch_number = models.CharField(max_length=100)
    expiry_date = models.DateField(null=True, blank=True)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.product} {self.batch_number}"


class StockMovement(models.Model):
    """Record stock in/out or transfer."""
    IN = 'IN'
    OUT = 'OUT'
    TRANSFER = 'TR'
    MOVEMENT_CHOICES = [
        (IN, 'Inbound'),
        (OUT, 'Outbound'),
        (TRANSFER, 'Transfer'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock_movements')
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_from')
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True, blank=True, related_name='stock_to')
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    batch = models.ForeignKey(StockLot, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True)


class InventoryAdjustment(models.Model):
    """Manual adjustment of inventory levels."""
    DAMAGE = 'damage'
    AUDIT = 'audit'
    OTHER = 'other'
    REASON_CHOICES = [
        (DAMAGE, 'Damage'),
        (AUDIT, 'Audit'),
        (OTHER, 'Other'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    qty = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)


class IdentifierType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class ProductSerial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    serial = models.CharField(max_length=100)
    is_sold = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'serial')

