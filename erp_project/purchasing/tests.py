from django.urls import reverse
from django.test import TestCase
import json
from django.contrib.auth import get_user_model
from accounts.models import Company, Role, UserRole, Permission
from inventory.models import (
    ProductCategory, ProductUnit, Product, Warehouse,
    IdentifierType, ProductSerial, StockMovement
)
from ledger.models import LedgerAccount, LedgerEntry
from .models import (
    Bank,
    Supplier,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    Payment,
    SupplierInvoice,
    QuotationRequest,
    QuotationRequestLine,
    PurchaseRequisition,
    ServiceItem,
    OfficeSupplyItem,
    AssetItem,
    ITSoftwareItem,
)

User = get_user_model()


class PurchasingLedgerTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='BuyCo', code='BC')
        self.user = User.objects.create_user(username='buyer', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = [
            'add_supplier', 'view_supplier',
            'add_purchaseorder', 'add_goodsreceipt', 'add_payment',
            'add_productcategory', 'add_product', 'add_productunit',
            'view_product',
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='buyer', password='pass')
        # ledger accounts
        for code in ['Inventory', 'Supplier', 'Supplier Advance', 'Cash', 'Bank']:
            LedgerAccount.objects.create(code=code, name=code, company=self.company)
        from ledger.utils import post_entry
        post_entry(self.company, 'open cash', [('Cash', 1000, 0)])
        self.bank = Bank.objects.create(name='TestBank', swift_code='TESTBANK')
        # identifier types
        self.ean = IdentifierType.objects.create(code='EAN13', name='EAN-13')
        self.serial = IdentifierType.objects.create(code='SER', name='Serial')

    def test_full_flow(self):
        cat = ProductCategory.objects.create(name='iPhone', company=self.company)
        cat.required_identifiers.set([self.ean, self.serial])
        unit = ProductUnit.objects.create(code='PCS', name='Pieces')
        prod = Product.objects.create(
            name='iPhone 15', sku='IP15', unit=unit, brand='Apple',
            category=cat, company=self.company, barcode='1234567890123',
            track_serial=True, vat_rate=5, sale_price=1000
        )
        sup = Supplier.objects.create(name='Apple', contact_person='CP', email='apple@example.com', phone='+14155550100', company=self.company, bank=self.bank)
        po = PurchaseOrder.objects.create(order_number='PO1', supplier=sup, company=self.company)
        PurchaseOrderLine.objects.create(purchase_order=po, product=prod, quantity=1, unit_price=1000)
        Payment.objects.create(
            purchase_order=po,
            amount=200,
            method=Payment.METHOD_CASH,
            is_advance=True,
            company=self.company,
            status=Payment.STATUS_APPROVED,
        )
        wh = Warehouse.objects.create(name='Main', location='A', company=self.company)
        GoodsReceipt.objects.create(purchase_order=po, product=prod, qty_received=1, warehouse=wh, ean='1234567890123', serial='SN1')
        Payment.objects.create(
            purchase_order=po,
            amount=800,
            method=Payment.METHOD_CASH,
            company=self.company,
            status=Payment.STATUS_APPROVED,
        )
        self.assertTrue(ProductSerial.objects.filter(product=prod, serial='SN1').exists())
        entries = LedgerEntry.objects.filter(company=self.company)
        self.assertEqual(entries.count(), 4)
        # advance payment
        adv = entries.order_by('id')[1]
        lines = list(adv.lines.values_list('account__code', 'debit', 'credit'))
        self.assertIn(('Supplier Advance', 200, 0), lines)
        self.assertIn(('Cash', 0, 200), lines)
        # goods receipt
        grn = entries.get(description='GRN PO1')
        grn_lines = list(grn.lines.values_list('account__code', 'debit', 'credit'))
        self.assertIn(('Inventory', 1000, 0), grn_lines)
        self.assertIn(('Supplier', 0, 1000), grn_lines)
        # final payment clears advance
        final = entries.order_by('id').last()
        final_lines = list(final.lines.values_list('account__code', 'debit', 'credit'))
        self.assertIn(('Supplier', 800, 0), final_lines)
        self.assertIn(('Supplier Advance', 0, 800), final_lines)


class IPhoneWorkflowIntegrationTests(TestCase):
    """End-to-end test covering iPhone onboarding and financial flow."""

    def setUp(self):
        self.company = Company.objects.create(name='PhoneCo', code='PC')
        self.user = User.objects.create_user(username='user', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = [
            'add_productcategory', 'add_productunit', 'add_product',
            'add_supplier', 'add_purchaseorder', 'add_goodsreceipt',
            'add_payment', 'add_warehouse', 'add_stockmovement',
            'view_stock_on_hand',
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='user', password='pass')

        for code in ['Inventory', 'Supplier', 'Supplier Advance', 'Cash', 'Bank']:
            LedgerAccount.objects.create(code=code, name=code, company=self.company)
        from ledger.utils import post_entry
        post_entry(self.company, 'open cash', [('Cash', 1000, 0)])
        self.bank = Bank.objects.create(name='TestBank', swift_code='TESTBANK')

        self.ean = IdentifierType.objects.create(code='EAN13', name='EAN-13')
        self.serial = IdentifierType.objects.create(code='SER', name='Serial')

    def test_full_workflow(self):
        # Create category with identifier requirements
        self.client.post(reverse('category_add'), {
            'name': 'iPhone',
            'parent': '',
            'identifiers': [self.ean.id, self.serial.id],
        })
        category = ProductCategory.objects.get(name='iPhone')

        # Create unit via quick add
        self.client.post(reverse('unit_quick_add'), {'code': 'PCS', 'name': 'Pieces'})
        unit = ProductUnit.objects.get(code='PCS')

        # Create product
        self.client.post(reverse('product_add'), {
            'name': 'iPhone 15',
            'sku': 'IP15',
            'unit': unit.id,
            'category': category.id,
            'brand': 'Apple',
            'barcode': '1234567890123',
            'vat_rate': '5',
            'sale_price': '1000',
            'track_serial': 'on',
        })
        product = Product.objects.get(sku='IP15')

        # Supplier
        self.client.post(reverse('supplier_add'), {
            'name': 'Apple',
            'contact_person': 'Tim',
            'phone': '+14155550111',
            'email': 'apple@example.com',
            'trade_license_number': '',
            'trn': '',
            'iban': '',
            'bank_name': 'TestBank',
            'swift_code': 'TESTBANK',
            'address': 'Cupertino',
        })
        supplier = Supplier.objects.filter(name='Apple').first()
        self.assertIsNotNone(supplier)

        # Purchase order
        self.client.post(reverse('purchase_order_add'), {
            'order_number': 'PO1',
            'supplier': supplier.id,
            'product': [product.id],
            'quantity': ['1'],
            'price': ['1000'],
        })
        po = PurchaseOrder.objects.get(order_number='PO1')
        line = po.lines.first()

        # Advance payment
        Payment.objects.create(
            purchase_order=po,
            amount=200,
            method=Payment.METHOD_CASH,
            is_advance=True,
            company=self.company,
            status=Payment.STATUS_APPROVED,
        )

        # Warehouse
        self.client.post(reverse('warehouse_add'), {'name': 'Main', 'location': 'A'})
        warehouse = Warehouse.objects.get(name='Main')

        # Goods receipt
        self.client.post(reverse('goods_receipt_add', args=[po.id, line.id]), {
            'qty': '1',
            'ean': '1234567890123',
            'serial': 'SN1',
            'warehouse': warehouse.id,
        })

        # Final payment
        Payment.objects.create(
            purchase_order=po,
            amount=800,
            method=Payment.METHOD_CASH,
            company=self.company,
            status=Payment.STATUS_APPROVED,
        )

        # Shelf transfer (internal)
        self.client.post(reverse('stock_movement_add'), {
            'product': product.id,
            'warehouse': warehouse.id,
            'qty': '1',
            'movement_type': StockMovement.TRANSFER,
        })

        # Assertions
        self.assertTrue(ProductSerial.objects.filter(product=product, serial='SN1').exists())
        entries = LedgerEntry.objects.filter(company=self.company)
        self.assertEqual(entries.count(), 4)
        # verify final payment cleared advance
        final = entries.order_by('id').last()
        lines = list(final.lines.values_list('account__code', 'debit', 'credit'))
        self.assertIn(('Supplier Advance', 0, 800), lines)
        # stock on hand
        soh = self.client.get(reverse('stock_on_hand'))
        self.assertContains(soh, 'iPhone 15')
        self.assertContains(soh, '1')

    def test_grn_identifier_validation(self):
        unit = ProductUnit.objects.create(code='PCS', name='Pieces')
        cat = ProductCategory.objects.create(name='Phones', company=self.company)
        cat.required_identifiers.set([self.ean, self.serial])
        prod = Product.objects.create(
            name='Phone',
            sku='P2',
            unit=unit,
            category=cat,
            barcode='123',
            track_serial=True,
            company=self.company,
        )
        sup = Supplier.objects.create(name='ACME', contact_person='CP2', email='acme@example.com', phone='+14155550101', company=self.company, bank=self.bank)
        po = PurchaseOrder.objects.create(order_number='POX', supplier=sup, company=self.company)
        line = PurchaseOrderLine.objects.create(purchase_order=po, product=prod, quantity=1, unit_price=10)
        wh = Warehouse.objects.create(name='W', location='L', company=self.company)
        url = reverse('goods_receipt_add', args=[po.id, line.id])
        resp = self.client.post(url, {'qty': '1', 'ean': 'bad', 'serial': 'S1', 'warehouse': wh.id})
        self.assertContains(resp, 'EAN mismatch')
        GoodsReceipt.objects.create(purchase_order=po, product=prod, qty_received=1, warehouse=wh, ean='123', serial='S1')
        resp = self.client.post(url, {'qty': '1', 'ean': '123', 'serial': 'S1', 'warehouse': wh.id})
        self.assertContains(resp, 'Serial duplicate')

    def test_insufficient_cash_blocks_payment(self):
        po = PurchaseOrder.objects.create(order_number='POZ', supplier=Supplier.objects.create(name='S', contact_person='CP3', email='s@example.com', phone='+14155550102', company=self.company, bank=self.bank), company=self.company)
        with self.assertRaises(ValueError):
            Payment.objects.create(purchase_order=po, amount=2000, method=Payment.METHOD_CASH, company=self.company, status=Payment.STATUS_APPROVED)


class QuotationRequestComplianceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='QCo', code='QC')
        self.user = User.objects.create_user(username='q', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_quotationrequest', 'view_product', 'add_supplier', 'add_product', 'add_productcategory', 'add_productunit']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='q', password='pass')
        self.bank = Bank.objects.create(name='TestBank', swift_code='TESTBANK')
        self.ean = IdentifierType.objects.create(code='EAN13', name='EAN-13')
        self.ser = IdentifierType.objects.create(code='SER', name='Serial')

    def test_quotation_enforces_identifiers(self):
        cat = ProductCategory.objects.create(name='Phone', company=self.company)
        cat.required_identifiers.set([self.ean, self.ser])
        unit = ProductUnit.objects.create(code='PCS', name='Pieces')
        prod = Product.objects.create(name='Phone1', sku='P1', unit=unit, company=self.company, category=cat, barcode='1111111111111', track_serial=True)
        sup = Supplier.objects.create(name='Sup', contact_person='CP4', email='sup@example.com', phone='+14155550103', company=self.company, bank=self.bank)
        url = reverse('quotation_add')
        resp = self.client.post(url, {
            'number': 'Q1', 'supplier': sup.id, 'product': prod.id,
            'quantity': '1', 'ean': 'wrong', 'serial_list': 'S1'
        })
        self.assertContains(resp, 'EAN mismatch')
        resp = self.client.post(url, {
            'number': 'Q1', 'supplier': sup.id, 'product': prod.id,
            'quantity': '2', 'ean': '1111111111111', 'serial_list': 'S1'
        })
        self.assertContains(resp, 'Serial count mismatch')
        resp = self.client.post(url, {
            'number': 'Q1', 'supplier': sup.id, 'product': prod.id,
            'quantity': '1', 'ean': '1111111111111', 'serial_list': 'S1'
        })
        self.assertEqual(resp.status_code, 302)


class PosScanTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='ScanCo', code='SC')
        self.user = User.objects.create_user(username='pos', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['view_product', 'add_product', 'add_productunit', 'add_productcategory']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='pos', password='pass')
        unit = ProductUnit.objects.create(code='PCS', name='Pieces')
        cat = ProductCategory.objects.create(name='Cat', company=self.company)
        self.product = Product.objects.create(name='Item', sku='IT', unit=unit, company=self.company, category=cat, barcode='9999999999999')
        ProductSerial.objects.create(product=self.product, serial='SER1')

    def test_scan_by_ean_and_serial(self):
        resp = self.client.post(reverse('pos_scan'), {'code': '9999999999999'})
        self.assertContains(resp, 'Item')
        resp = self.client.post(reverse('pos_scan'), {'code': 'SER1'})
        self.assertContains(resp, 'Item')


class SupplierEnhancementTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='SupCo', code='SC')
        self.user = User.objects.create_user(username='sup', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = [
            'add_supplier', 'change_supplier', 'view_supplier',
            'can_discontinue_supplier',
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='sup', password='pass')
        self.bank = Bank.objects.create(name='TestBank', swift_code='TESTBANK')

    def test_create_with_description(self):
        url = reverse('supplier_add')
        self.client.post(url, {
            'name': 'ACME',
            'description': 'Widgets',
            'contact_person': 'Bob',
            'phone': '+14155550123',
            'email': 'acme@example.com',
            'trade_license_number': '',
            'trn': '',
            'iban': '',
            'bank_name': 'TestBank',
            'swift_code': 'TESTBANK',
            'address': 'A',
        })
        supplier = Supplier.objects.get(name='ACME')
        self.assertEqual(supplier.description, 'Widgets')

    def test_update_email_triggers_verification(self):
        supplier = Supplier.objects.create(name='ACME', description='', contact_person='CP', email='a@x.com', phone='+14155550110', company=self.company, bank=self.bank, is_verified=True)
        url = reverse('supplier_edit', args=[supplier.id])
        resp = self.client.post(url, {
            'name': 'ACME',
            'description': '',
            'contact_person': 'CP',
            'phone': '+14155550111',
            'email': 'new@example.com',
            'trade_license_number': '',
            'trn': '',
            'iban': '',
            'bank_name': 'TestBank',
            'swift_code': 'TESTBANK',
            'address': 'A',
        })
        self.assertEqual(resp.status_code, 302)
        supplier.refresh_from_db()
        self.assertFalse(supplier.is_verified)
        self.assertEqual(supplier.otps.count(), 1)

    def test_toggle_requires_permission(self):
        supplier = Supplier.objects.create(name='X', contact_person='CP', company=self.company)
        # remove permission
        role = Role.objects.get(name='Admin')
        perm = Permission.objects.get(codename='can_discontinue_supplier')
        role.permissions.remove(perm)
        url = reverse('supplier_toggle', args=[supplier.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)

    def test_list_search_filter_sort(self):
        Supplier.objects.create(name='AAA', contact_person='c1', company=self.company)
        Supplier.objects.create(name='BBB', contact_person='c2', company=self.company, is_connected=False)
        resp = self.client.get(reverse('supplier_list'), {'q': 'AAA'})
        self.assertContains(resp, 'AAA')
        self.assertNotContains(resp, 'BBB')
        resp = self.client.get(reverse('supplier_list'), {'is_connected': 'False'})
        self.assertContains(resp, 'BBB')

    def test_bank_ajax_search_and_create(self):
        Bank.objects.create(name='AjaxBank', swift_code='AJAX12345')
        resp = self.client.get(reverse('bank_search'), {'q': 'Ajax'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('AjaxBank', resp.json()[0]['name'])
        # create supplier with new bank
        self.client.post(reverse('supplier_add'), {
            'name': 'NewSup',
            'contact_person': 'CP',
            'email': 'n@e.com',
            'bank_name': 'BrandNewBank',
            'swift_code': 'BRAND123',
        })
        self.assertTrue(Bank.objects.filter(name='BrandNewBank').exists())

    def test_supplier_form_uses_select2(self):
        resp = self.client.get(reverse('supplier_add'))
        self.assertContains(resp, 'select2')

    def test_supplier_update_form_uses_select2(self):
        supplier = Supplier.objects.create(name='S1', contact_person='CP', email='s1@example.com', phone='+10000000000', company=self.company)
        resp = self.client.get(reverse('supplier_edit', args=[supplier.id]))
        self.assertContains(resp, 'select2')

    def test_master_item_search_endpoints(self):
        ServiceItem.objects.create(name='Clean', unit=ProductUnit.objects.create(code='JOB', name='Job'), company=self.company)
        OfficeSupplyItem.objects.create(name='Paper', unit=ProductUnit.objects.create(code='EA', name='Each'), company=self.company)
        AssetItem.objects.create(name='Printer', unit=ProductUnit.objects.create(code='EA2', name='Each'), company=self.company)
        ITSoftwareItem.objects.create(name='Antivirus', unit=ProductUnit.objects.create(code='LIC', name='License'), company=self.company)
        resp = self.client.get(reverse('service_search'), {'q': 'Clean'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Clean', resp.json()['results'][0]['text'])
        resp = self.client.get(reverse('office_supply_search'), {'q': 'Paper'})
        self.assertIn('Paper', resp.json()['results'][0]['text'])
        resp = self.client.get(reverse('asset_item_search'), {'q': 'Print'})
        self.assertIn('Printer', resp.json()['results'][0]['text'])
        resp = self.client.get(reverse('it_item_search'), {'q': 'Anti'})
        self.assertIn('Antivirus', resp.json()['results'][0]['text'])



class PurchaseRequisitionTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='PRCo', code='PR')
        self.user = User.objects.create_user(username='req', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = [
            'add_purchaserequisition', 'view_purchaserequisition', 'approve_purchaserequisition',
            'add_productcategory', 'add_productunit', 'add_product'
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='req', password='pass')
        self.unit = ProductUnit.objects.create(code='PCS', name='Pieces')
        self.cat = ProductCategory.objects.create(name='Cat', company=self.company)
        self.product = Product.objects.create(name='Item', sku='IT1', unit=self.unit, company=self.company, category=self.cat)

    def test_create_and_approve_requisition(self):
        resp = self.client.post(reverse('requisition_add'), {
            'request_type': PurchaseRequisition.TYPE_PRODUCT,
            'product': self.product.id,
            'quantity': '1',
        })
        self.assertEqual(resp.status_code, 302)
        pr = PurchaseRequisition.objects.first()
        self.assertTrue(pr.number.startswith(f"{self.company.code}-PR"))
        self.assertEqual(pr.status, PurchaseRequisition.PENDING)
        approver = User.objects.create_user(username='approver', password='pass', company=self.company)
        UserRole.objects.create(user=approver, role=Role.objects.get(name='Admin'), company=self.company)
        self.client.login(username='approver', password='pass')
        resp = self.client.post(reverse('requisition_approve', args=[pr.id]), {'action': 'approve'})
        self.assertEqual(resp.status_code, 302)
        pr.refresh_from_db()
        self.assertEqual(pr.status, PurchaseRequisition.APPROVED)
        self.client.login(username='req', password='pass')

    def test_requisition_multiple_lines(self):
        data = [{"type": "Service", "description": "Install", "quantity": "1", "unit": "job"}]
        resp = self.client.post(reverse('requisition_add'), {
            'request_type': PurchaseRequisition.TYPE_SERVICE,
            'product': self.product.id,
            'quantity': '1',
            'items_json': json.dumps(data),
            'justification': 'Need service'
        })
        self.assertEqual(resp.status_code, 302)
        pr = PurchaseRequisition.objects.first()
        self.assertEqual(len(pr.items), 1)

    def test_requisition_form_get_contains_json(self):
        resp = self.client.get(reverse('requisition_add'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'prod-data')

    def test_requisition_form_has_help_and_summary(self):
        resp = self.client.get(reverse('requisition_add'))
        self.assertContains(resp, 'Use this form to request')
        self.assertContains(resp, 'summary-text')

    def test_auto_number_increment(self):
        self.client.post(reverse('requisition_add'), {
            'request_type': PurchaseRequisition.TYPE_PRODUCT,
            'product': self.product.id,
            'quantity': '1',
        })
        self.client.post(reverse('requisition_add'), {
            'request_type': PurchaseRequisition.TYPE_PRODUCT,
            'product': self.product.id,
            'quantity': '1',
        })
        nums = list(PurchaseRequisition.objects.values_list('number', flat=True).order_by('id'))
        self.assertEqual(nums[0][-4:], '0001')
        self.assertEqual(nums[1][-4:], '0002')

    def test_creator_cannot_approve(self):
        self.client.post(reverse('requisition_add'), {
            'request_type': PurchaseRequisition.TYPE_PRODUCT,
            'product': self.product.id,
            'quantity': '1',
        })
        pr = PurchaseRequisition.objects.first()
        resp = self.client.post(reverse('requisition_approve', args=[pr.id]), {'action': 'approve'})
        pr.refresh_from_db()
        self.assertEqual(pr.status, PurchaseRequisition.PENDING)

    def test_pdf_requires_permission(self):
        self.client.post(reverse('requisition_add'), {
            'request_type': PurchaseRequisition.TYPE_PRODUCT,
            'product': self.product.id,
            'quantity': '1',
        })
        pr = PurchaseRequisition.objects.first()
        approver = User.objects.create_user(username='approver2', password='pass', company=self.company)
        UserRole.objects.create(user=approver, role=Role.objects.get(name='Admin'), company=self.company)
        self.client.login(username='approver2', password='pass')
        self.client.post(reverse('requisition_approve', args=[pr.id]), {'action': 'approve'})
        self.client.login(username='req', password='pass')
        resp = self.client.get(reverse('requisition_pdf', args=[pr.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')


class ProcurementExtrasTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='EXCo', code='EX')
        self.user = User.objects.create_user(username='ex', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = [
            'add_quotationrequest', 'add_purchaseorder', 'add_supplierinvoice',
            'add_payment', 'approve_payment', 'view_payment',
            'add_productcategory', 'add_productunit', 'add_product',
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='ex', password='pass')
        self.unit = ProductUnit.objects.create(code='PCS', name='Pieces')
        self.cat = ProductCategory.objects.create(name='Cat', company=self.company)
        self.product = Product.objects.create(name='Item', sku='IT2', unit=self.unit, company=self.company, category=self.cat, sale_price=10)
        self.supplier = Supplier.objects.create(name='Sup', contact_person='CP', phone='+111', email='s@e.com', company=self.company)
        for code in ['Inventory', 'Supplier', 'Cash']:
            LedgerAccount.objects.create(code=code, name=code, company=self.company)
        from ledger.utils import post_entry
        post_entry(self.company, 'open cash', [('Cash', 100, 0)])

    def test_select_quotation_creates_po(self):
        resp = self.client.post(reverse('quotation_add'), {
            'number': 'Q1', 'supplier': self.supplier.id, 'product': self.product.id,
            'quantity': '1', 'unit_price': '8'
        })
        line = QuotationRequestLine.objects.first()
        self.client.post(reverse('quotation_select', args=[line.id]))
        self.assertTrue(PurchaseOrder.objects.filter(supplier=self.supplier).exists())

    def test_invoice_match_view(self):
        po = PurchaseOrder.objects.create(order_number='PO99', supplier=self.supplier, company=self.company)
        PurchaseOrderLine.objects.create(purchase_order=po, product=self.product, quantity=1, unit_price=10)
        GoodsReceipt.objects.create(purchase_order=po, product=self.product, qty_received=1, warehouse=Warehouse.objects.create(name='W', location='A', company=self.company), ean='', serial='S1')
        inv = SupplierInvoice.objects.create(number='INV1', purchase_order=po, amount=10, company=self.company)
        resp = self.client.get(reverse('invoice_match', args=[inv.id]))
        self.assertContains(resp, 'All documents match')

    def test_payment_approval_posts_ledger(self):
        for code in ['Supplier', 'Cash']:
            LedgerAccount.objects.get_or_create(code=code, name=code, company=self.company)
        Payment.objects.create(purchase_order=None, amount=5, method=Payment.METHOD_CASH, company=self.company)
        payment = Payment.objects.first()
        resp = self.client.post(reverse('payment_approve', args=[payment.id]), {'action': 'approve'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(payment.approvals.count(), 1)


class ProcurementCycleIntegrationTests(TestCase):
    """Integration test covering the full procurement cycle."""

    def setUp(self):
        self.company = Company.objects.create(name='FlowCo', code='FC')
        self.user = User.objects.create_user(
            username='proc', password='pass', company=self.company
        )
        role = Role.objects.get(name='Admin')
        perms = [
            'add_purchaserequisition', 'approve_purchaserequisition',
            'add_quotationrequest', 'add_purchaseorder', 'ack_purchaseorder',
            'add_goodsreceipt', 'add_supplierinvoice', 'view_supplierinvoice',
            'add_payment', 'approve_payment', 'view_payment',
            'add_productcategory', 'add_productunit', 'add_product',
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='proc', password='pass')

        self.unit = ProductUnit.objects.create(code='PCS', name='Pieces')
        self.cat = ProductCategory.objects.create(name='Cat', company=self.company)
        self.product = Product.objects.create(
            name='Item', sku='IT3', unit=self.unit,
            company=self.company, category=self.cat, sale_price=8,
            barcode='1234567890123'
        )
        self.supplier = Supplier.objects.create(
            name='Sup', contact_person='CP', phone='+123',
            email='sup@example.com', company=self.company
        )
        for code in ['Inventory', 'Supplier', 'Supplier Advance', 'Cash']:
            LedgerAccount.objects.create(code=code, name=code, company=self.company)
        from ledger.utils import post_entry
        post_entry(self.company, 'open cash', [('Cash', 100, 0)])

    def test_full_procurement_flow(self):
        # 1. Create requisition
        self.client.post(reverse('requisition_add'), {
            'request_type': PurchaseRequisition.TYPE_PRODUCT,
            'product': self.product.id,
            'quantity': '1'
        })
        pr = PurchaseRequisition.objects.first()
        self.assertTrue(pr.number.endswith('0001'))
        self.assertEqual(pr.status, PurchaseRequisition.PENDING)

        # 2. Approve requisition by different user
        approver = User.objects.create_user(username='approver3', password='pass', company=self.company)
        UserRole.objects.create(user=approver, role=Role.objects.get(name='Admin'), company=self.company)
        self.client.login(username='approver3', password='pass')
        self.client.post(reverse('requisition_approve', args=[pr.id]), {'action': 'approve'})
        self.client.login(username='proc', password='pass')
        pr.refresh_from_db()
        self.assertEqual(pr.status, PurchaseRequisition.APPROVED)

        # 3. Request quotation
        self.client.post(reverse('quotation_add'), {
            'number': 'Q1', 'supplier': self.supplier.id,
            'product': self.product.id, 'quantity': '1', 'unit_price': '8'
        })
        line = QuotationRequestLine.objects.first()

        # 4. Select quotation to create PO
        self.client.post(reverse('quotation_select', args=[line.id]))
        po = PurchaseOrder.objects.first()
        self.assertIsNotNone(po)

        # 5. Acknowledge PO
        self.client.post(reverse('purchase_order_ack', args=[po.id]))
        po.refresh_from_db()
        self.assertTrue(po.acknowledged)

        # 6. Goods receipt
        wh = Warehouse.objects.create(name='Main', location='A', company=self.company)
        line_obj = po.lines.first()
        self.client.post(reverse('goods_receipt_add', args=[po.id, line_obj.id]), {
            'qty': '1', 'ean': self.product.barcode, 'serial': 'S1', 'warehouse': wh.id
        })
        self.assertEqual(GoodsReceipt.objects.filter(purchase_order=po).count(), 1)

        # 7. Supplier invoice
        self.client.post(reverse('invoice_add'), {
            'number': 'INV1', 'po': po.id, 'amount': '8'
        })
        invoice = SupplierInvoice.objects.get(number='INV1')

        # 8. Three-way match check
        resp = self.client.get(reverse('invoice_match', args=[invoice.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'All documents match')

        # 9. Create payment
        self.client.post(reverse('payment_add'), {
            'po': po.id, 'amount': '8', 'method': Payment.METHOD_CASH
        })
        payment = Payment.objects.get(purchase_order=po)
        self.assertEqual(payment.status, Payment.STATUS_PENDING)

        # 10. Approve payment
        self.client.post(reverse('payment_approve', args=[payment.id]), {'action': 'approve'})
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.STATUS_APPROVED)
        self.assertEqual(payment.approvals.count(), 1)

        # 11. Ledger entries created
        entries = LedgerEntry.objects.filter(company=self.company)
        self.assertGreaterEqual(entries.count(), 3)


class ServiceItemTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='SvcCo', code='SV')
        self.user = User.objects.create_user(username='svc', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_serviceitem', 'view_serviceitem', 'change_serviceitem', 'delete_serviceitem', 'add_productunit']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='svc', password='pass')
        self.unit = ProductUnit.objects.create(code='JOB', name='Job')

    def test_create_list_edit_delete_service(self):
        resp = self.client.post(reverse('service_add'), {'name': 'Install', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item = ServiceItem.objects.get(name='Install')
        resp = self.client.get(reverse('service_list'))
        self.assertContains(resp, 'Install')
        resp = self.client.post(reverse('service_edit', args=[item.id]), {'name': 'Fix', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.name, 'Fix')
        resp = self.client.post(reverse('service_delete', args=[item.id]))
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertFalse(item.is_active)

class OfficeSupplyItemTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='OfficeCo', code='OF')
        self.user = User.objects.create_user(username='ofc', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_officesupplyitem', 'view_officesupplyitem', 'change_officesupplyitem', 'delete_officesupplyitem', 'add_productunit']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='ofc', password='pass')
        self.unit = ProductUnit.objects.create(code='EA', name='Each')

    def test_create_list_edit_delete_office_supply(self):
        resp = self.client.post(reverse('office_supply_add'), {'name': 'Pen', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item = OfficeSupplyItem.objects.get(name='Pen')
        resp = self.client.get(reverse('office_supply_list'))
        self.assertContains(resp, 'Pen')
        resp = self.client.post(reverse('office_supply_edit', args=[item.id]), {'name': 'Pencil', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.name, 'Pencil')
        resp = self.client.post(reverse('office_supply_delete', args=[item.id]))
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertFalse(item.is_active)


class AssetItemTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='AssetCo', code='AC')
        self.user = User.objects.create_user(username='ast', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_assetitem', 'view_assetitem', 'change_assetitem', 'delete_assetitem', 'add_productunit']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='ast', password='pass')
        self.unit = ProductUnit.objects.create(code='EA', name='Each')

    def test_create_list_edit_delete_asset_item(self):
        resp = self.client.post(reverse('asset_item_add'), {'name': 'Desk', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item = AssetItem.objects.get(name='Desk')
        resp = self.client.get(reverse('asset_item_list'))
        self.assertContains(resp, 'Desk')
        resp = self.client.post(reverse('asset_item_edit', args=[item.id]), {'name': 'Chair', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.name, 'Chair')
        resp = self.client.post(reverse('asset_item_delete', args=[item.id]))
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertFalse(item.is_active)


class ITSoftwareItemTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='ITCo', code='IT')
        self.user = User.objects.create_user(username='it', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_itsoftwareitem', 'view_itsoftwareitem', 'change_itsoftwareitem', 'delete_itsoftwareitem', 'add_productunit']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='it', password='pass')
        self.unit = ProductUnit.objects.create(code='LIC', name='License')

    def test_create_list_edit_delete_it_item(self):
        resp = self.client.post(reverse('it_item_add'), {'name': 'Software', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item = ITSoftwareItem.objects.get(name='Software')
        resp = self.client.get(reverse('it_item_list'))
        self.assertContains(resp, 'Software')
        resp = self.client.post(reverse('it_item_edit', args=[item.id]), {'name': 'App', 'unit': self.unit.id})
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.name, 'App')
        resp = self.client.post(reverse('it_item_delete', args=[item.id]))
        self.assertEqual(resp.status_code, 302)
        item.refresh_from_db()
        self.assertFalse(item.is_active)
