from django.contrib import admin
from .models import Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, Payment

admin.site.register(Supplier)
admin.site.register(PurchaseOrder)
admin.site.register(PurchaseOrderLine)
admin.site.register(GoodsReceipt)
admin.site.register(Payment)
