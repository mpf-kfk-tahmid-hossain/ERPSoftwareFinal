from django.urls import path
from .views import (
    WarehouseListView, WarehouseCreateView, WarehouseUpdateView,
    ProductCategoryListView, ProductCategoryCreateView, ProductCategoryUpdateView,
    ProductUnitListView, ProductUnitCreateView,
    ProductListView, ProductCreateView,
    StockLotListView, StockLotCreateView,
    StockMovementListView, StockMovementCreateView,
    InventoryAdjustmentListView, InventoryAdjustmentCreateView,
    stock_on_hand,
)

urlpatterns = [
    path('warehouses/', WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouses/add/', WarehouseCreateView.as_view(), name='warehouse_add'),
    path('warehouses/<int:pk>/edit/', WarehouseUpdateView.as_view(), name='warehouse_edit'),
    path('categories/', ProductCategoryListView.as_view(), name='category_list'),
    path('categories/add/', ProductCategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', ProductCategoryUpdateView.as_view(), name='category_edit'),
    path('units/', ProductUnitListView.as_view(), name='unit_list'),
    path('units/add/', ProductUnitCreateView.as_view(), name='unit_add'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/add/', ProductCreateView.as_view(), name='product_add'),
    path('stock-lots/', StockLotListView.as_view(), name='stock_lot_list'),
    path('stock-lots/add/', StockLotCreateView.as_view(), name='stock_lot_add'),
    path('stock-movements/', StockMovementListView.as_view(), name='stock_movement_list'),
    path('stock-movements/add/', StockMovementCreateView.as_view(), name='stock_movement_add'),
    path('inventory-adjustments/', InventoryAdjustmentListView.as_view(), name='inventory_adjustment_list'),
    path('inventory-adjustments/add/', InventoryAdjustmentCreateView.as_view(), name='inventory_adjustment_add'),
    path('stock-on-hand/', stock_on_hand, name='stock_on_hand'),
]
