from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
import random
from accounts.utils import require_permission, user_has_permission, log_action
from .models import (
    Bank,
    Supplier,
    SupplierOTP,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    QuotationRequest,
    QuotationRequestLine,
)
from .utils import (
    validate_phone,
    validate_trade_license,
    validate_trn,
    validate_iban,
    validate_swift,
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
        context = {
            'name': '',
            'contact_person': '',
            'phone': '',
            'email': '',
            'trade_license_number': '',
            'trn': '',
            'iban': '',
            'bank_name': '',
            'swift_code': '',
            'address': '',
            'banks': Bank.objects.all(),
        }
        return render(request, 'supplier_form.html', context)

    def post(self, request):
        fields = ['name', 'contact_person', 'phone', 'email', 'trade_license_number', 'trn', 'iban', 'bank_name', 'swift_code', 'address']
        data = {f: request.POST.get(f, '').strip() for f in fields}
        errors = []
        if not data['name']:
            errors.append('Name required')
        if not data['contact_person']:
            errors.append('Contact person required')
        if data['phone'] and not validate_phone(data['phone']):
            errors.append('Invalid phone number')
        if Supplier.objects.filter(email=data['email']).exists():
            errors.append('Email already exists')
        if data['phone'] and Supplier.objects.filter(phone=data['phone']).exists():
            errors.append('Phone already exists')
        if data['trade_license_number'] and not validate_trade_license(data['trade_license_number']):
            errors.append('Invalid trade license number')
        if data['trade_license_number'] and Supplier.objects.filter(trade_license_number=data['trade_license_number']).exists():
            errors.append('Trade license number exists')
        if data['trn'] and not validate_trn(data['trn']):
            errors.append('Invalid TRN')
        if data['trn'] and Supplier.objects.filter(trn=data['trn']).exists():
            errors.append('TRN exists')
        if data['iban'] and not validate_iban(data['iban']):
            errors.append('Invalid IBAN')
        if data['iban'] and Supplier.objects.filter(iban=data['iban']).exists():
            errors.append('IBAN exists')
        bank = None
        if data['bank_name'] or data['swift_code']:
            if not data['bank_name'] or not data['swift_code']:
                errors.append('Bank name and SWIFT required together')
            elif not validate_swift(data['swift_code']):
                errors.append('Invalid SWIFT code')
            else:
                if Bank.objects.filter(swift_code=data['swift_code']).exclude(name=data['bank_name']).exists():
                    errors.append('SWIFT code already used by another bank')
                bank, created = Bank.objects.get_or_create(
                    name=data['bank_name'],
                    defaults={'swift_code': data['swift_code']},
                )
                if not created and bank.swift_code != data['swift_code']:
                    errors.append('Bank exists with different SWIFT code')
        if errors:
            data['error'] = '; '.join(errors)
            data['banks'] = Bank.objects.all()
            return render(request, 'supplier_form.html', data)

        supplier = Supplier.objects.create(
            name=data['name'],
            contact_person=data['contact_person'],
            phone=data['phone'],
            email=data['email'],
            trade_license_number=data['trade_license_number'],
            trn=data['trn'],
            iban=data['iban'],
            bank=bank,
            address=data['address'],
            company=request.user.company,
        )
        code = f"{random.randint(100000, 999999)}"
        SupplierOTP.objects.create(supplier=supplier, code=code)
        send_mail(
            'Supplier Verification',
            f'Your verification code is {code}',
            'noreply@example.com',
            [supplier.email],
            fail_silently=True,
        )
        log_action(request.user, 'create_supplier', details={'name': supplier.name}, company=request.user.company)
        return redirect('supplier_detail', pk=supplier.pk)


@method_decorator(require_permission('view_supplier'), name='dispatch')
class SupplierDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'supplier_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = get_object_or_404(Supplier, pk=self.kwargs['pk'], company=self.request.user.company)
        context['supplier'] = supplier
        context['bank'] = supplier.bank
        context['can_toggle'] = user_has_permission(self.request.user, 'change_supplier')
        context['can_verify'] = not supplier.is_verified
        return context


@method_decorator(require_permission('change_supplier'), name='dispatch')
class SupplierToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
        supplier.is_connected = not supplier.is_connected
        supplier.save()
        return redirect('supplier_detail', pk=pk)


@method_decorator(require_permission('change_supplier'), name='dispatch')
class SupplierVerifyView(LoginRequiredMixin, View):
    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
        code = request.POST.get('otp', '').strip()
        otp = supplier.otps.filter(code=code, is_used=False).order_by('-created_at').first()
        if otp and otp.is_valid():
            supplier.is_verified = True
            supplier.save()
            otp.is_used = True
            otp.save()
            return redirect('supplier_detail', pk=pk)
        return render(request, 'supplier_detail.html', {'supplier': supplier, 'error': 'Invalid OTP', 'can_toggle': user_has_permission(request.user, 'change_supplier'), 'can_verify': True})


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
