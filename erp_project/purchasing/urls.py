from django.urls import path
from . import views

urlpatterns = [
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_add'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/<int:pk>/toggle/', views.SupplierToggleView.as_view(), name='supplier_toggle'),
    path('suppliers/<int:pk>/verify/', views.SupplierVerifyView.as_view(), name='supplier_verify'),
    path('purchase-orders/add/', views.PurchaseOrderCreateView.as_view(), name='purchase_order_add'),
    path('purchase-orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase_order_detail'),
    path('purchase-orders/<int:po_id>/lines/<int:line_id>/receive/', views.GoodsReceiptCreateView.as_view(), name='goods_receipt_add'),
    path('quotations/add/', views.QuotationRequestCreateView.as_view(), name='quotation_add'),
]
