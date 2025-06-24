from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
import random
from accounts.utils import (
    AdvancedListMixin,
    require_permission,
    user_has_permission,
    log_action,
)
from .models import (
    Bank,
    Supplier,
    SupplierOTP,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    Payment,
    PaymentApproval,
    SupplierInvoice,
    SupplierEvaluation,
    QuotationRequest,
    QuotationRequestLine,
    PurchaseRequisition,
    PurchaseRequisitionApproval,
)
from .utils import (
    validate_phone,
    validate_trade_license,
    validate_trn,
    validate_iban,
    validate_swift,
)
from inventory.models import Product, Warehouse, ProductSerial
from django.http import JsonResponse


class SupplierListView(LoginRequiredMixin, AdvancedListMixin, TemplateView):
    template_name = 'supplier_list.html'
    model = Supplier
    search_fields = ['name', 'contact_person', 'phone', 'email']
    filter_fields = ['is_verified', 'is_connected']
    default_sort = 'name'

    def base_queryset(self):
        return Supplier.objects.filter(company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = [
            {
                'name': 'is_verified',
                'label': 'Verified',
                'options': [
                    {'val': '', 'label': 'All'},
                    {'val': 'True', 'label': 'Verified'},
                    {'val': 'False', 'label': 'Unverified'},
                ],
                'current': self.request.GET.get('is_verified', ''),
            },
            {
                'name': 'is_connected',
                'label': 'Status',
                'options': [
                    {'val': '', 'label': 'All'},
                    {'val': 'True', 'label': 'Active'},
                    {'val': 'False', 'label': 'Discontinued'},
                ],
                'current': self.request.GET.get('is_connected', ''),
            },
        ]
        context['sort_options'] = [
            ('name', 'Name'),
            ('contact_person', 'Contact'),
        ]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_supplier'] = user_has_permission(self.request.user, 'add_supplier')
        return context


@method_decorator(require_permission('add_supplier'), name='dispatch')
class SupplierCreateView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'title': 'Add Supplier',
            'name': '',
            'description': '',
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
        data['description'] = request.POST.get('description', '').strip()
        errors = {}
        if not data['name']:
            errors['name'] = 'Name required'
        if not data['contact_person']:
            errors['contact_person'] = 'Contact person required'
        if data['phone'] and not validate_phone(data['phone']):
            errors['phone'] = 'Invalid phone number'
        if Supplier.objects.filter(email=data['email']).exists():
            errors['email'] = 'Email already exists'
        if data['phone'] and Supplier.objects.filter(phone=data['phone']).exists():
            errors['phone'] = 'Phone already exists'
        if data['trade_license_number'] and not validate_trade_license(data['trade_license_number']):
            errors['trade_license_number'] = 'Invalid trade license number'
        if data['trade_license_number'] and Supplier.objects.filter(trade_license_number=data['trade_license_number']).exists():
            errors['trade_license_number'] = 'Trade license number exists'
        if data['trn'] and not validate_trn(data['trn']):
            errors['trn'] = 'Invalid TRN'
        if data['trn'] and Supplier.objects.filter(trn=data['trn']).exists():
            errors['trn'] = 'TRN exists'
        if data['iban'] and not validate_iban(data['iban']):
            errors['iban'] = 'Invalid IBAN'
        if data['iban'] and Supplier.objects.filter(iban=data['iban']).exists():
            errors['iban'] = 'IBAN exists'
        bank = None
        if data['bank_name'] or data['swift_code']:
            if not data['bank_name'] or not data['swift_code']:
                errors['bank_name'] = 'Bank name and SWIFT required together'
            elif not validate_swift(data['swift_code']):
                errors['swift_code'] = 'Invalid SWIFT code'
            else:
                if Bank.objects.filter(swift_code=data['swift_code']).exclude(name=data['bank_name']).exists():
                    errors['swift_code'] = 'SWIFT code already used by another bank'
                bank, created = Bank.objects.get_or_create(
                    name=data['bank_name'],
                    defaults={'swift_code': data['swift_code']},
                )
                if not created and bank.swift_code != data['swift_code']:
                    errors['swift_code'] = 'Bank exists with different SWIFT code'
        if errors:
            data['errors'] = errors
            data['banks'] = Bank.objects.all()
            data['title'] = 'Add Supplier'
            return render(request, 'supplier_form.html', data)

        supplier = Supplier.objects.create(
            name=data['name'],
            description=data['description'],
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
        messages.success(request, 'Supplier added successfully')
        return redirect('supplier_detail', pk=supplier.pk)


@method_decorator(require_permission('view_supplier'), name='dispatch')
class SupplierDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'supplier_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = get_object_or_404(Supplier, pk=self.kwargs['pk'], company=self.request.user.company)
        context['supplier'] = supplier
        context['bank'] = supplier.bank
        context['can_toggle'] = user_has_permission(self.request.user, 'can_discontinue_supplier')
        context['can_verify'] = not supplier.is_verified
        show = self.request.session.pop('show_otp_for', None)
        context['show_otp_modal'] = show == supplier.id
        return context


@method_decorator(require_permission('can_discontinue_supplier'), name='dispatch')
class SupplierToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
        supplier.is_connected = not supplier.is_connected
        supplier.save()
        if supplier.is_connected:
            messages.success(request, 'Supplier reactivated successfully')
        else:
            messages.success(request, 'Supplier discontinued successfully')
        return redirect('supplier_detail', pk=pk)


@method_decorator(require_permission('change_supplier'), name='dispatch')
class SupplierUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
        context = {
            'title': 'Update Supplier',
            'name': supplier.name,
            'description': supplier.description,
            'contact_person': supplier.contact_person,
            'phone': supplier.phone or '',
            'email': supplier.email or '',
            'trade_license_number': supplier.trade_license_number or '',
            'trn': supplier.trn or '',
            'iban': supplier.iban or '',
            'bank_name': supplier.bank.name if supplier.bank else '',
            'swift_code': supplier.bank.swift_code if supplier.bank else '',
            'address': supplier.address,
            'banks': Bank.objects.all(),
            'supplier': supplier,
        }
        return render(request, 'supplier_form.html', context)

    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
        fields = ['name', 'contact_person', 'phone', 'email', 'trade_license_number', 'trn', 'iban', 'bank_name', 'swift_code', 'address', 'description']
        data = {f: request.POST.get(f, '').strip() for f in fields}
        errors = {}
        if not data['name']:
            errors['name'] = 'Name required'
        if not data['contact_person']:
            errors['contact_person'] = 'Contact person required'
        if data['phone'] and not validate_phone(data['phone']):
            errors['phone'] = 'Invalid phone number'
        if data['email'] and Supplier.objects.filter(email=data['email']).exclude(pk=supplier.pk).exists():
            errors['email'] = 'Email already exists'
        if data['phone'] and Supplier.objects.filter(phone=data['phone']).exclude(pk=supplier.pk).exists():
            errors['phone'] = 'Phone already exists'
        if data['trade_license_number'] and not validate_trade_license(data['trade_license_number']):
            errors['trade_license_number'] = 'Invalid trade license number'
        if data['trade_license_number'] and Supplier.objects.filter(trade_license_number=data['trade_license_number']).exclude(pk=supplier.pk).exists():
            errors['trade_license_number'] = 'Trade license number exists'
        if data['trn'] and not validate_trn(data['trn']):
            errors['trn'] = 'Invalid TRN'
        if data['trn'] and Supplier.objects.filter(trn=data['trn']).exclude(pk=supplier.pk).exists():
            errors['trn'] = 'TRN exists'
        if data['iban'] and not validate_iban(data['iban']):
            errors['iban'] = 'Invalid IBAN'
        if data['iban'] and Supplier.objects.filter(iban=data['iban']).exclude(pk=supplier.pk).exists():
            errors['iban'] = 'IBAN exists'
        bank = None
        if data['bank_name'] or data['swift_code']:
            if not data['bank_name'] or not data['swift_code']:
                errors['bank_name'] = 'Bank name and SWIFT required together'
            elif not validate_swift(data['swift_code']):
                errors['swift_code'] = 'Invalid SWIFT code'
            else:
                if Bank.objects.filter(swift_code=data['swift_code']).exclude(name=data['bank_name']).exists():
                    errors['swift_code'] = 'SWIFT code already used by another bank'
                bank, created = Bank.objects.get_or_create(
                    name=data['bank_name'],
                    defaults={'swift_code': data['swift_code']},
                )
                if not created and bank.swift_code != data['swift_code']:
                    errors['swift_code'] = 'Bank exists with different SWIFT code'
        if errors:
            data['errors'] = errors
            data['banks'] = Bank.objects.all()
            data['supplier'] = supplier
            data['title'] = 'Update Supplier'
            return render(request, 'supplier_form.html', data)

        changed_contact = data['email'] != (supplier.email or '') or data['phone'] != (supplier.phone or '')
        supplier.name = data['name']
        supplier.description = data['description']
        supplier.contact_person = data['contact_person']
        supplier.phone = data['phone'] or None
        supplier.email = data['email'] or None
        supplier.trade_license_number = data['trade_license_number'] or None
        supplier.trn = data['trn'] or None
        supplier.iban = data['iban'] or None
        supplier.bank = bank
        supplier.address = data['address']
        if changed_contact:
            supplier.is_verified = False
            code = f"{random.randint(100000, 999999)}"
            SupplierOTP.objects.create(supplier=supplier, code=code)
            send_mail(
                'Supplier Verification',
                f'Your verification code is {code}',
                'noreply@example.com',
                [supplier.email],
                fail_silently=True,
            )
        supplier.save()
        log_action(request.user, 'update_supplier', details={'id': supplier.id}, company=request.user.company)
        messages.success(request, 'Supplier updated successfully')
        return redirect('supplier_detail', pk=supplier.pk)


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
        return render(request, 'supplier_detail.html', {'supplier': supplier, 'error': 'Invalid OTP', 'can_toggle': user_has_permission(request.user, 'can_discontinue_supplier'), 'can_verify': True})


@method_decorator(require_permission('change_supplier'), name='dispatch')
class SupplierRequestOTPView(LoginRequiredMixin, View):
    def post(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk, company=request.user.company)
        code = f"{random.randint(100000, 999999)}"
        SupplierOTP.objects.create(supplier=supplier, code=code)
        send_mail(
            'Supplier Verification',
            f'Your verification code is {code}',
            'noreply@example.com',
            [supplier.email],
            fail_silently=True,
        )
        request.session['show_otp_for'] = supplier.id
        messages.success(request, 'OTP sent to supplier')
        return redirect('supplier_detail', pk=pk)


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
        context['can_ack'] = user_has_permission(self.request.user, 'ack_purchaseorder') and not po.acknowledged
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


@method_decorator(require_permission('ack_purchaseorder'), name='dispatch')
class PurchaseOrderAcknowledgeView(LoginRequiredMixin, View):
    """Mark purchase order as acknowledged by supplier."""

    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk, company=request.user.company)
        if not po.acknowledged:
            po.acknowledged = True
            po.acknowledged_at = timezone.now()
            po.save()
            send_mail(
                'PO Acknowledged',
                f'Purchase order {po.order_number} acknowledged',
                'noreply@example.com',
                [request.user.email],
                fail_silently=True,
            )
        return redirect('purchase_order_detail', pk=pk)


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
        price = request.POST.get('unit_price', '0').strip()
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
            unit_price=price or 0,
            ean=ean,
            serial_list=serials,
        )
        log_action(request.user, 'create_quotation', details={'number': number}, company=request.user.company)
        return redirect('purchase_order_add')


class BankSearchView(LoginRequiredMixin, View):
    """Return bank names matching a query for AJAX search."""

    def get(self, request):
        q = request.GET.get('q', '')
        banks = Bank.objects.filter(name__icontains=q)[:10]
        data = [{'name': b.name} for b in banks]
        return JsonResponse(data, safe=False)

class PurchaseRequisitionListView(LoginRequiredMixin, AdvancedListMixin, TemplateView):
    template_name = 'requisition_list.html'
    model = PurchaseRequisition
    search_fields = ['number', 'product__name', 'requester__username']
    filter_fields = ['status']
    default_sort = '-created_at'

    def base_queryset(self):
        return PurchaseRequisition.objects.filter(company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = [
            {
                'name': 'status',
                'label': 'Status',
                'options': [
                    {'val': '', 'label': 'All'},
                    {'val': PurchaseRequisition.PENDING, 'label': 'Pending'},
                    {'val': PurchaseRequisition.APPROVED, 'label': 'Approved'},
                    {'val': PurchaseRequisition.REJECTED, 'label': 'Rejected'},
                ],
                'current': self.request.GET.get('status', ''),
            }
        ]
        context['sort_options'] = [
            ('created_at', 'Date'),
            ('number', 'Number'),
        ]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add'] = user_has_permission(self.request.user, 'add_purchaserequisition')
        return context


@method_decorator(require_permission('add_purchaserequisition'), name='dispatch')
class PurchaseRequisitionCreateView(LoginRequiredMixin, View):
    def get(self, request):
        products = Product.objects.filter(company=request.user.company)
        return render(request, 'requisition_form.html', {'products': products})

    def post(self, request):
        number = request.POST.get('number', '').strip()
        product_id = request.POST.get('product')
        qty = request.POST.get('quantity', '').strip()
        spec = request.POST.get('specification', '').strip()
        just = request.POST.get('justification', '').strip()
        if not number or not product_id or not qty:
            products = Product.objects.filter(company=request.user.company)
            return render(request, 'requisition_form.html', {'products': products, 'error': 'All fields required'})
        if PurchaseRequisition.objects.filter(number=number, company=request.user.company).exists():
            products = Product.objects.filter(company=request.user.company)
            return render(request, 'requisition_form.html', {'products': products, 'error': 'Number exists'})
        product = get_object_or_404(Product, pk=product_id, company=request.user.company)
        pr = PurchaseRequisition.objects.create(
            number=number,
            product=product,
            quantity=qty,
            specification=spec,
            justification=just,
            requester=request.user,
            status=PurchaseRequisition.PENDING,
            company=request.user.company,
        )
        log_action(request.user, 'create_pr', details={'number': number}, company=request.user.company)
        return redirect('requisition_detail', pk=pr.pk)


class PurchaseRequisitionDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'requisition_detail.html'

    def get_context_data(self, **kwargs):
        pr = get_object_or_404(PurchaseRequisition, pk=self.kwargs['pk'], company=self.request.user.company)
        context = super().get_context_data(**kwargs)
        context['pr'] = pr
        context['can_approve'] = user_has_permission(self.request.user, 'approve_purchaserequisition') and pr.status == PurchaseRequisition.PENDING
        return context


@method_decorator(require_permission('approve_purchaserequisition'), name='dispatch')
class PurchaseRequisitionApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        pr = get_object_or_404(PurchaseRequisition, pk=pk, company=request.user.company)
        if pr.status != PurchaseRequisition.PENDING:
            return redirect('requisition_detail', pk=pk)
        action = request.POST.get('action')
        comment = request.POST.get('comment', '').strip()
        approved = action == 'approve'
        pr.status = PurchaseRequisition.APPROVED if approved else PurchaseRequisition.REJECTED
        pr.save()
        PurchaseRequisitionApproval.objects.create(
            requisition=pr,
            approver=request.user,
            approved=approved,
            comment=comment,
            approved_at=timezone.now(),
        )
        log_action(request.user, 'approve_pr', details={'id': pr.id, 'approved': approved}, company=request.user.company)
        return redirect('requisition_detail', pk=pk)


class QuotationComparisonView(LoginRequiredMixin, TemplateView):
    """List quotations for comparison and allow selection."""

    template_name = 'quotation_compare.html'

    def get_context_data(self, **kwargs):
        product_id = self.request.GET.get('product')
        lines = QuotationRequestLine.objects.filter(quotation__company=self.request.user.company, selected=False)
        if product_id:
            lines = lines.filter(product__id=product_id)
        lines = lines.select_related('quotation', 'product', 'quotation__supplier').order_by('unit_price')
        products = Product.objects.filter(company=self.request.user.company)
        return {
            'lines': lines,
            'products': products,
            'product_id': int(product_id) if product_id else '',
        }


@method_decorator(require_permission('add_purchaseorder'), name='dispatch')
class QuotationSelectView(LoginRequiredMixin, View):
    """Create a PO from the chosen quotation line."""

    def post(self, request, line_id):
        line = get_object_or_404(
            QuotationRequestLine,
            pk=line_id,
            quotation__company=request.user.company,
        )
        if line.selected:
            return redirect('quotation_compare')
        line.selected = True
        line.save()
        po = PurchaseOrder.objects.create(
            order_number=f"PO{random.randint(1000,9999)}",
            supplier=line.quotation.supplier,
            company=request.user.company,
        )
        PurchaseOrderLine.objects.create(
            purchase_order=po,
            product=line.product,
            quantity=line.quantity,
            unit_price=line.unit_price,
        )
        send_mail(
            'Quotation Selected',
            f'PO {po.order_number} created from quotation {line.quotation.number}',
            'noreply@example.com',
            [request.user.email],
            fail_silently=True,
        )
        return redirect('purchase_order_detail', pk=po.pk)


class SupplierInvoiceListView(LoginRequiredMixin, TemplateView):
    template_name = 'invoice_list.html'

    def get_context_data(self, **kwargs):
        invoices = SupplierInvoice.objects.filter(company=self.request.user.company)
        return {'invoices': invoices}


@method_decorator(require_permission('add_supplierinvoice'), name='dispatch')
class SupplierInvoiceCreateView(LoginRequiredMixin, View):
    def get(self, request):
        pos = PurchaseOrder.objects.filter(company=request.user.company)
        return render(request, 'invoice_form.html', {'pos': pos})

    def post(self, request):
        number = request.POST.get('number', '').strip()
        po = get_object_or_404(PurchaseOrder, pk=request.POST.get('po'), company=request.user.company)
        amount = request.POST.get('amount', '0').strip()
        file = request.FILES.get('file')
        if not number or not amount:
            pos = PurchaseOrder.objects.filter(company=request.user.company)
            return render(request, 'invoice_form.html', {'pos': pos, 'error': 'All fields required'})
        inv = SupplierInvoice.objects.create(number=number, purchase_order=po, amount=amount, file=file or None, company=request.user.company)
        send_mail('Invoice Submitted', f'Invoice {number} submitted', 'noreply@example.com', [request.user.email], fail_silently=True)
        return redirect('invoice_list')


class InvoiceMatchView(LoginRequiredMixin, TemplateView):
    template_name = 'invoice_match.html'

    def get_context_data(self, **kwargs):
        invoice = get_object_or_404(SupplierInvoice, pk=self.kwargs['pk'], company=self.request.user.company)
        po = invoice.purchase_order
        po_total = sum(l.quantity * l.unit_price for l in po.lines.all())
        grn_total = sum(gr.qty_received * gr.product.sale_price for gr in GoodsReceipt.objects.filter(purchase_order=po))
        match = po_total == grn_total == float(invoice.amount)
        return {'invoice': invoice, 'po_total': po_total, 'grn_total': grn_total, 'match': match}


@method_decorator(require_permission('approve_payment'), name='dispatch')
class PaymentApprovalView(LoginRequiredMixin, View):
    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, company=request.user.company)
        action = request.POST.get('action')
        approved = action == 'approve'
        payment.status = Payment.STATUS_APPROVED if approved else Payment.STATUS_REJECTED
        payment.save()
        PaymentApproval.objects.create(payment=payment, approver=request.user, approved=approved, comment=request.POST.get('comment', ''))
        if approved:
            payment.post_ledger_entry()
        send_mail('Payment Approval', f'Payment {payment.id} {payment.status}', 'noreply@example.com', [request.user.email], fail_silently=True)
        return redirect('payment_list')


class PaymentListView(LoginRequiredMixin, TemplateView):
    template_name = 'payment_list.html'

    def get_context_data(self, **kwargs):
        payments = Payment.objects.filter(company=self.request.user.company)
        return {'payments': payments}


@method_decorator(require_permission('add_payment'), name='dispatch')
class PaymentCreateView(LoginRequiredMixin, View):
    def get(self, request):
        pos = PurchaseOrder.objects.filter(company=request.user.company)
        return render(request, 'payment_form.html', {'pos': pos})

    def post(self, request):
        po_id = request.POST.get('po')
        po = get_object_or_404(PurchaseOrder, pk=po_id, company=request.user.company) if po_id else None
        amount = request.POST.get('amount', '0').strip()
        method = request.POST.get('method', Payment.METHOD_CASH)
        Payment.objects.create(purchase_order=po, amount=amount, method=method, company=request.user.company)
        send_mail('Payment Request', f'Payment for {amount} submitted', 'noreply@example.com', [request.user.email], fail_silently=True)
        return redirect('payment_list')


@method_decorator(require_permission('add_supplierevaluation'), name='dispatch')
class SupplierEvaluationCreateView(LoginRequiredMixin, View):
    def get(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, pk=supplier_id, company=request.user.company)
        return render(request, 'evaluation_form.html', {'supplier': supplier})

    def post(self, request, supplier_id):
        supplier = get_object_or_404(Supplier, pk=supplier_id, company=request.user.company)
        score = request.POST.get('score', '').strip()
        SupplierEvaluation.objects.create(supplier=supplier, score=score, comments=request.POST.get('comments', ''), company=request.user.company)
        return redirect('supplier_detail', pk=supplier_id)
