from django.urls import path
from . import views

urlpatterns = [
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('purchase-orders/add/', views.PurchaseOrderCreateView.as_view(), name='purchase_order_add'),
    path('purchase-orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase_order_detail'),
    path('purchase-orders/<int:po_id>/lines/<int:line_id>/receive/', views.GoodsReceiptCreateView.as_view(), name='goods_receipt_add'),
    path('quotations/add/', views.QuotationRequestCreateView.as_view(), name='quotation_add'),
]
