from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from accounts.utils import require_permission, user_has_permission, log_action
from .models import (
    Supplier,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    QuotationRequest,
    QuotationRequestLine,
)
from inventory.models import Product, Warehouse, ProductSerial


class SupplierListView(LoginRequiredMixin, TemplateView):
    template_name = 'supplier_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        context['suppliers'] = Supplier.objects.filter(company=company)
        context['can_add_supplier'] = user_has_permission(self.request.user, 'add_supplier')
        return context


@method_decorator(require_permission('add_supplier'), name='dispatch')
class SupplierCreateView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'supplier_form.html', {'name': '', 'contact_info': ''})

    def post(self, request):
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'supplier_form.html', {'error': 'Name required', 'name': name, 'contact_info': request.POST.get('contact_info', '')})
        Supplier.objects.create(
            name=name,
            contact_info=request.POST.get('contact_info', ''),
            company=request.user.company,
        )
        log_action(request.user, 'create_supplier', details={'name': name}, company=request.user.company)
        return redirect('supplier_list')


@method_decorator(require_permission('add_purchaseorder'), name='dispatch')
class PurchaseOrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        suppliers = Supplier.objects.filter(company=request.user.company)
        products = Product.objects.filter(company=request.user.company)
        return render(request, 'purchase_order_form.html', {'suppliers': suppliers, 'products': products})

    def post(self, request):
        supplier = get_object_or_404(Supplier, pk=request.POST.get('supplier'), company=request.user.company)
        number = request.POST.get('order_number', '').strip()
        if not number:
            suppliers = Supplier.objects.filter(company=request.user.company)
            products = Product.objects.filter(company=request.user.company)
            return render(request, 'purchase_order_form.html', {'error': 'Number required', 'suppliers': suppliers, 'products': products})
        po = PurchaseOrder.objects.create(
            order_number=number, supplier=supplier, company=request.user.company
        )
        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')
        prices = request.POST.getlist('price')
        for pid, qty, price in zip(product_ids, quantities, prices):
            if pid:
                prod = get_object_or_404(Product, pk=pid, company=request.user.company)
                PurchaseOrderLine.objects.create(purchase_order=po, product=prod, quantity=qty or 0, unit_price=price or 0)
        log_action(request.user, 'create_po', details={'number': number}, company=request.user.company)
        return redirect('purchase_order_detail', pk=po.pk)


class PurchaseOrderDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'purchase_order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'], company=self.request.user.company)
        context['po'] = po
        context['can_receive'] = user_has_permission(self.request.user, 'add_goodsreceipt')
        return context


@method_decorator(require_permission('add_goodsreceipt'), name='dispatch')
class GoodsReceiptCreateView(LoginRequiredMixin, View):
    def get(self, request, po_id, line_id):
        line = get_object_or_404(PurchaseOrderLine, pk=line_id, purchase_order__company=request.user.company)
        warehouses = Warehouse.objects.filter(company=request.user.company)
        return render(request, 'goods_receipt_form.html', {'line': line, 'warehouses': warehouses})

    def post(self, request, po_id, line_id):
        line = get_object_or_404(PurchaseOrderLine, pk=line_id, purchase_order__company=request.user.company)
        warehouse = get_object_or_404(Warehouse, pk=request.POST.get('warehouse'), company=request.user.company)
        ean = request.POST.get('ean', '').strip()
        serial = request.POST.get('serial', '').strip()
        qty = request.POST.get('qty', '0').strip()
        if not ean or not serial or not qty:
            warehouses = Warehouse.objects.filter(company=request.user.company)
            return render(request, 'goods_receipt_form.html', {'line': line, 'warehouses': warehouses, 'error': 'All fields required'})
        if ean != line.product.barcode:
            warehouses = Warehouse.objects.filter(company=request.user.company)
            return render(request, 'goods_receipt_form.html', {'line': line, 'warehouses': warehouses, 'error': 'EAN mismatch'})
        if ProductSerial.objects.filter(product=line.product, serial=serial).exists():
            warehouses = Warehouse.objects.filter(company=request.user.company)
            return render(request, 'goods_receipt_form.html', {'line': line, 'warehouses': warehouses, 'error': 'Serial duplicate'})
        GoodsReceipt.objects.create(
            purchase_order=line.purchase_order,
            product=line.product,
            qty_received=qty,
            warehouse=warehouse,
            ean=ean,
            serial=serial,
        )
        log_action(
            request.user,
            'create_grn',
            details={'po': line.purchase_order.order_number},
            company=request.user.company,
        )
        return redirect('purchase_order_detail', pk=line.purchase_order.pk)


@method_decorator(require_permission('add_quotationrequest'), name='dispatch')
class QuotationRequestCreateView(LoginRequiredMixin, View):
    """Create a quotation request ensuring identifier compliance."""

    def get(self, request):
        suppliers = Supplier.objects.filter(company=request.user.company)
        products = Product.objects.filter(company=request.user.company)
        return render(
            request,
            'quotation_request_form.html',
            {'suppliers': suppliers, 'products': products},
        )

    def post(self, request):
        supplier = get_object_or_404(
            Supplier, pk=request.POST.get('supplier'), company=request.user.company
        )
        number = request.POST.get('number', '').strip()
        if not number:
            suppliers = Supplier.objects.filter(company=request.user.company)
            products = Product.objects.filter(company=request.user.company)
            return render(
                request,
                'quotation_request_form.html',
                {
                    'suppliers': suppliers,
                    'products': products,
                    'error': 'Number required',
                },
            )
        product = get_object_or_404(
            Product, pk=request.POST.get('product'), company=request.user.company
        )
        qty = request.POST.get('quantity', '0').strip()
        ean = request.POST.get('ean', '').strip()
        serials = request.POST.get('serial_list', '').strip()
        # Identifier compliance
        required = product.category.required_identifiers.all() if product.category else []
        codes = {r.code for r in required}
        if 'EAN13' in codes and ean != product.barcode:
            suppliers = Supplier.objects.filter(company=request.user.company)
            products = Product.objects.filter(company=request.user.company)
            return render(
                request,
                'quotation_request_form.html',
                {
                    'suppliers': suppliers,
                    'products': products,
                    'error': 'EAN mismatch',
                },
            )
        if 'SER' in codes:
            serial_list = [s.strip() for s in serials.split(',') if s.strip()]
            if len(serial_list) != int(qty or 0):
                suppliers = Supplier.objects.filter(company=request.user.company)
                products = Product.objects.filter(company=request.user.company)
                return render(
                    request,
                    'quotation_request_form.html',
                    {
                        'suppliers': suppliers,
                        'products': products,
                        'error': 'Serial count mismatch',
                    },
                )
        qr = QuotationRequest.objects.create(
            number=number, supplier=supplier, company=request.user.company
        )
        QuotationRequestLine.objects.create(
            quotation=qr,
            product=product,
            quantity=qty or 0,
            ean=ean,
            serial_list=serials,
        )
        log_action(request.user, 'create_quotation', details={'number': number}, company=request.user.company)
        return redirect('purchase_order_add')
