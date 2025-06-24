from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Company, Role, UserRole, Permission, AuditLog
from .models import (
    Warehouse,
    ProductCategory,
    ProductUnit,
    Product,
    StockLot,
    StockMovement,
    InventoryAdjustment,
    ProductSerial,
)

User = get_user_model()


class WarehouseViewTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='InvCo', code='IC', address='')
        self.user = User.objects.create_user(username='inv', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        # grant new permissions to admin role for tests
        perms = [
            'add_warehouse', 'view_warehouse', 'change_warehouse',
            'add_productcategory', 'view_productcategory', 'change_productcategory'
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='inv', password='pass')

    def test_create_warehouse(self):
        resp = self.client.post(reverse('warehouse_add'), {'name': 'Main', 'location': 'A'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Warehouse.objects.filter(name='Main', company=self.company).exists())

    def test_get_warehouse_forms(self):
        resp = self.client.get(reverse('warehouse_add'))
        self.assertEqual(resp.status_code, 200)
        wh = Warehouse.objects.create(name='EditW', location='Loc', company=self.company)
        resp = self.client.get(reverse('warehouse_edit', args=[wh.id]))
        self.assertContains(resp, 'value="EditW"')
        self.assertContains(resp, 'value="Loc"')


class CategoryViewTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='InvCo', code='IC', address='')
        self.user = User.objects.create_user(username='inv', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_productcategory', 'view_productcategory', 'change_productcategory']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='inv', password='pass')

    def test_create_category(self):
        resp = self.client.post(reverse('category_add'), {'name': 'Cat1', 'code': ''})
        self.assertEqual(resp.status_code, 302)
        cat = ProductCategory.objects.get(name='Cat1', company=self.company)
        self.assertTrue(cat.code)

    def test_create_category_ignores_new_parent_marker(self):
        resp = self.client.post(reverse('category_add'), {'name': 'CatNew', 'parent': '__new__'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ProductCategory.objects.filter(name='CatNew', parent__isnull=True, company=self.company).exists())

    def test_duplicate_category_rejected(self):
        ProductCategory.objects.create(name='Unique', company=self.company)
        resp = self.client.post(reverse('category_add'), {'name': 'Unique'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ProductCategory.objects.filter(name='Unique', company=self.company).count(), 1)

    def test_get_category_forms(self):
        resp = self.client.get(reverse('category_add'))
        self.assertEqual(resp.status_code, 200)
        cat = ProductCategory.objects.create(name='Old', company=self.company)
        resp = self.client.get(reverse('category_edit', args=[cat.id]))
        self.assertContains(resp, 'value="Old"')

    def test_category_children_endpoint(self):
        parent = ProductCategory.objects.create(name='Root', company=self.company)
        ProductCategory.objects.create(name='Child', parent=parent, company=self.company)
        resp = self.client.get(reverse('category_children'), {'parent': parent.id, 'level': 2})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Child')

    def test_level_two_dropdown_rendered(self):
        parent = ProductCategory.objects.create(name='Root', company=self.company)
        ProductCategory.objects.create(name='ChildA', parent=parent, company=self.company)
        resp = self.client.get(reverse('category_children'), {'parent': parent.id, 'level': 2})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data[0]['name'], 'ChildA')

    def test_quick_add(self):
        resp = self.client.post(reverse('category_quick_add'), {'name': 'Quick'})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(ProductCategory.objects.filter(name='Quick', company=self.company).exists())

    def test_quick_add_duplicate(self):
        ProductCategory.objects.create(name='Dup', company=self.company)
        resp = self.client.post(reverse('category_quick_add'), {'name': 'Dup'})
        self.assertEqual(resp.status_code, 400)


class CategoryManageTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='TreeCo', code='TC', address='')
        self.user = User.objects.create_user(username='tree', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_productcategory', 'view_productcategory', 'change_productcategory', 'discontinue_productcategory']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='tree', password='pass')

    def test_move_and_rename_delete(self):
        root = ProductCategory.objects.create(name='Root', company=self.company)
        child = ProductCategory.objects.create(name='Child', company=self.company)
        resp = self.client.post(reverse('category_move', args=[child.id]), {'parent': root.id})
        self.assertEqual(resp.status_code, 200)
        child.refresh_from_db()
        self.assertEqual(child.parent, root)
        resp = self.client.post(reverse('category_rename', args=[child.id]), {'name': 'New'})
        self.assertEqual(resp.status_code, 200)
        child.refresh_from_db()
        self.assertEqual(child.name, 'New')
        resp = self.client.post(reverse('category_discontinue', args=[child.id]))
        self.assertEqual(resp.status_code, 200)
        child.refresh_from_db()
        self.assertTrue(child.is_discontinued)

    def test_rename_duplicate_rejected(self):
        cat1 = ProductCategory.objects.create(name='A', company=self.company)
        cat2 = ProductCategory.objects.create(name='B', company=self.company)
        resp = self.client.post(reverse('category_rename', args=[cat2.id]), {'name': 'A'})
        self.assertEqual(resp.status_code, 400)

    def test_circular_move_blocked(self):
        root = ProductCategory.objects.create(name='Root', company=self.company)
        child = ProductCategory.objects.create(name='Child', parent=root, company=self.company)
        resp = self.client.post(reverse('category_move', args=[root.id]), {'parent': child.id})
        self.assertEqual(resp.status_code, 400)




class ProductFlowTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='ProdCo', code='PC', address='')
        self.user = User.objects.create_user(username='prod', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = [
            'add_productunit',
            'add_product', 'view_product',
            'add_stocklot', 'view_stocklot',
            'add_stockmovement', 'view_stockmovement',
            'add_inventoryadjustment', 'view_inventoryadjustment',
            'view_stock_on_hand', 'change_productcategory'
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='prod', password='pass')

    def test_full_product_flow(self):
        # create unit via quick add
        resp_u = self.client.post(reverse('unit_quick_add'), {'code': 'PCS', 'name': 'Pieces'})
        self.assertEqual(resp_u.status_code, 201)
        unit = ProductUnit.objects.get(code='PCS')
        # create category and product
        cat = ProductCategory.objects.create(name='Cat', company=self.company)
        self.client.post(reverse('product_add'), {'name': 'Prod1', 'unit': unit.id, 'category': cat.id})
        prod = Product.objects.first()
        # create warehouse and stock lot
        wh = Warehouse.objects.create(name='WH', location='L', company=self.company)
        self.client.post(reverse('stock_lot_add'), {
            'product': prod.id,
            'warehouse': wh.id,
            'batch_number': 'B1',
            'qty': '5'
        })
        self.assertTrue(StockLot.objects.filter(batch_number='B1').exists())
        # stock movement
        self.client.post(reverse('stock_movement_add'), {
            'product': prod.id,
            'warehouse': wh.id,
            'qty': '2',
            'movement_type': 'OUT'
        })
        self.assertEqual(StockMovement.objects.count(), 1)
        # adjustment
        self.client.post(reverse('inventory_adjustment_add'), {
            'product': prod.id,
            'warehouse': wh.id,
            'qty': '1',
            'reason': 'audit'
        })
        self.assertEqual(InventoryAdjustment.objects.count(), 1)
        # stock on hand
        resp = self.client.get(reverse('stock_on_hand'))
        self.assertEqual(resp.status_code, 200)

    def test_auto_sku_generation(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        cat = ProductCategory.objects.create(name='Leaf', company=self.company)
        resp = self.client.post(reverse('product_add'), {
            'name': 'AutoProd', 'unit': unit.id, 'category': cat.id
        })
        self.assertEqual(resp.status_code, 302)
        prod = Product.objects.get(name='AutoProd')
        self.assertTrue(prod.sku.startswith(self.company.code))


    def test_product_detail_view_shows_specs_and_inventory(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        product = Product.objects.create(name='Widget', sku='W99', unit=unit, company=self.company, specs={'General': {'Color': 'Red'}})
        wh = Warehouse.objects.create(name='Main', location='A', company=self.company)
        StockLot.objects.create(product=product, warehouse=wh, batch_number='B1', qty=7)
        resp = self.client.get(reverse('product_detail', args=[product.id]))
        self.assertContains(resp, 'Widget')
        self.assertContains(resp, 'Color')
        self.assertContains(resp, 'Red')
        self.assertContains(resp, '7')

    def test_product_quick_view_endpoint(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        product = Product.objects.create(name='Mini', sku='M1', unit=unit, company=self.company)
        resp = self.client.get(reverse('product_quick_view', args=[product.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Mini')

    def test_product_search_and_category_filter(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        cat = ProductCategory.objects.create(name='Tools', company=self.company)
        p1 = Product.objects.create(name='Hammer', sku='H1', unit=unit, company=self.company, category=cat, specs={'General': {'Color': 'Red'}})
        p2 = Product.objects.create(name='Drill', sku='D1', unit=unit, company=self.company, specs={'General': {'Color': 'Blue'}})
        resp = self.client.get(reverse('product_list'), {'q': 'Red'})
        self.assertContains(resp, 'Hammer')
        self.assertNotContains(resp, 'Drill')
        resp = self.client.get(reverse('product_list'), {'category': cat.id})
        self.assertContains(resp, 'Hammer')
        self.assertNotContains(resp, 'Drill')

    def test_initial_inventory_on_create(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        wh = Warehouse.objects.create(name='Main', location='A', company=self.company)
        self.client.post(reverse('product_add'), {
            'name': 'Saw', 'unit': unit.id,
            'init_wh': [str(wh.id)], 'init_qty': ['5']
        })
        self.assertEqual(StockLot.objects.filter(warehouse=wh).count(), 1)


class InventoryEndToEndTests(TestCase):
    """Full workflow test covering product setup and stock operations."""

    def setUp(self):
        self.company = Company.objects.create(name='FlowCo', code='FC', address='')
        self.user = User.objects.create_user(username='flow', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = [
            'add_productcategory', 'view_productcategory',
            'add_productunit',
            'add_product', 'view_product',
            'add_warehouse', 'view_warehouse',
            'add_stocklot', 'view_stocklot',
            'add_stockmovement', 'view_stockmovement',
            'add_inventoryadjustment', 'view_inventoryadjustment',
            'view_stock_on_hand', 'view_auditlog'
        ]
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='flow', password='pass')

    def test_end_to_end_inventory_flow(self):
        # create category
        self.client.post(reverse('category_add'), {'name': 'Electronics'})
        category = ProductCategory.objects.get(name='Electronics', company=self.company)

        # create unit via quick add
        self.client.post(reverse('unit_quick_add'), {'code': 'PCS', 'name': 'Pieces'})
        unit = ProductUnit.objects.get(code='PCS')

        # create product
        self.client.post(reverse('product_add'), {
            'name': 'Widget',
            'unit': unit.id,
            'category': category.id,
        })
        product = Product.objects.first()

        # create warehouse
        self.client.post(reverse('warehouse_add'), {'name': 'Main', 'location': 'A'})
        warehouse = Warehouse.objects.get(name='Main', company=self.company)

        # create stock lot
        self.client.post(reverse('stock_lot_add'), {
            'product': product.id,
            'warehouse': warehouse.id,
            'batch_number': 'B1',
            'qty': '5',
        })
        self.assertTrue(StockLot.objects.filter(batch_number='B1').exists())

        # stock movement
        self.client.post(reverse('stock_movement_add'), {
            'product': product.id,
            'warehouse': warehouse.id,
            'qty': '2',
            'movement_type': StockMovement.OUT,
        })

        # inventory adjustment
        self.client.post(reverse('inventory_adjustment_add'), {
            'product': product.id,
            'warehouse': warehouse.id,
            'qty': '1',
            'reason': InventoryAdjustment.AUDIT,
        })

        # verify stock on hand calculation
        resp = self.client.get(reverse('stock_on_hand'))
        self.assertContains(resp, 'Widget')
        self.assertContains(resp, '4')

        # verify audit logs created
        log_actions = ['create_unit', 'create_product', 'create_lot', 'stock_move', 'inventory_adjust']
        for action in log_actions:
            self.assertTrue(AuditLog.objects.filter(action=action, actor=self.user).exists())

        # audit log list accessible
        log_resp = self.client.get(reverse('audit_log_list'))
        self.assertEqual(log_resp.status_code, 200)


class SKUGenerationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='AutoCo', code='AC01')
        self.user = User.objects.create_user(username='auto', password='pass', company=self.company)
        role = Role.objects.get(name='Admin')
        perms = ['add_productunit', 'add_product', 'view_product']
        for codename in perms:
            perm, _ = Permission.objects.get_or_create(codename=codename)
            role.permissions.add(perm)
        UserRole.objects.create(user=self.user, role=role, company=self.company)
        self.client.login(username='auto', password='pass')

    def test_serial_increment_per_category(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        cat = ProductCategory.objects.create(name='Leaf', company=self.company)
        self.client.post(reverse('product_add'), {'name': 'P1', 'unit': unit.id, 'category': cat.id})
        self.client.post(reverse('product_add'), {'name': 'P2', 'unit': unit.id, 'category': cat.id})
        p1 = Product.objects.get(name='P1')
        p2 = Product.objects.get(name='P2')
        self.assertTrue(p1.sku.endswith('-000001'))
        self.assertTrue(p2.sku.endswith('-000002'))

    def test_serial_tracking_uses_single_sku(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        cat = ProductCategory.objects.create(name='Leaf', company=self.company)
        prod = Product.objects.create(name='Track', unit=unit, category=cat, company=self.company, track_serial=True)
        ProductSerial.objects.create(product=prod, serial='A1')
        ProductSerial.objects.create(product=prod, serial='A2')
        self.assertEqual(ProductSerial.objects.filter(product=prod).count(), 2)
        for ser in ProductSerial.objects.filter(product=prod):
            self.assertEqual(ser.product.sku, prod.sku)

    def test_migration_function_generates_skus(self):
        unit = ProductUnit.objects.create(code='BX', name='Box')
        cat = ProductCategory.objects.create(name='Leaf', company=self.company)
        prod = Product.objects.create(name='Old', sku='OLD1', unit=unit, category=cat, company=self.company)
        from importlib import import_module
        from django.apps import apps
        migrate = import_module('inventory.migrations.0010_migrate_skus').migrate_skus
        migrate(apps, None)
        prod.refresh_from_db()
        self.assertEqual(prod.legacy_sku, 'OLD1')
        self.assertTrue(prod.sku.startswith(self.company.code))


class TemplateValueSanityTests(TestCase):
    """Ensure templates do not use fallback expressions in value attributes."""

    def test_templates_do_not_use_default_filter_in_values(self):
        import re
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent / 'templates'
        pattern = re.compile(r'value="{{[^"}]*\|')
        for tpl in base.rglob('*.html'):
            content = tpl.read_text()
            matches = pattern.findall(content)
            self.assertFalse(matches, f"Unexpected default filter in {tpl}")


class NoHTMXUsageTests(TestCase):
    """Ensure templates do not contain hx-get or hx-post attributes."""

    def test_templates_do_not_use_htmx_get_post(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent / 'templates'
        for tpl in base.rglob('*.html'):
            content = tpl.read_text()
            self.assertNotIn('hx-get', content, f"hx-get found in {tpl}")
            self.assertNotIn('hx-post', content, f"hx-post found in {tpl}")

