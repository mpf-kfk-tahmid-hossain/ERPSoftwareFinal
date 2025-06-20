from django.contrib import admin
from .models import (
    Warehouse, ProductCategory, ProductUnit, Product, StockLot,
    StockMovement, InventoryAdjustment
)

admin.site.register(Warehouse)
admin.site.register(ProductCategory)
admin.site.register(ProductUnit)
admin.site.register(Product)
admin.site.register(StockLot)
admin.site.register(StockMovement)
admin.site.register(InventoryAdjustment)
