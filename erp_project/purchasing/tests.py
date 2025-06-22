from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Company, Role, UserRole, Permission
from inventory.models import (
    ProductCategory, ProductUnit, Product, Warehouse,
    IdentifierType, ProductSerial, StockMovement
)
from ledger.models import LedgerAccount, LedgerEntry
from .models import Bank, Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, Payment

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
        )
        wh = Warehouse.objects.create(name='Main', location='A', company=self.company)
        GoodsReceipt.objects.create(purchase_order=po, product=prod, qty_received=1, warehouse=wh, ean='1234567890123', serial='SN1')
        Payment.objects.create(
            purchase_order=po,
            amount=800,
            method=Payment.METHOD_CASH,
            company=self.company,
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
            Payment.objects.create(purchase_order=po, amount=2000, method=Payment.METHOD_CASH, company=self.company)


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


