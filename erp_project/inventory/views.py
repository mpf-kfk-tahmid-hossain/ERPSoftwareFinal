from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse

from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.db.models import Sum
from accounts.utils import user_has_permission

from accounts.models import UserRole

from accounts.utils import AdvancedListMixin, require_permission, log_action
from .models import (
    Warehouse,
    ProductCategory,
    ProductUnit,
    Product,
    StockLot,
    StockMovement,
    InventoryAdjustment,
)


@method_decorator(require_permission('view_warehouse'), name='dispatch')
class WarehouseListView(AdvancedListMixin, TemplateView):
    """List warehouses for the current company."""

    template_name = 'warehouse_list.html'
    model = Warehouse
    search_fields = ['name', 'location']
    default_sort = 'name'

    def base_queryset(self):
        return Warehouse.objects.filter(company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = []
        context['sort_options'] = [
            ('name', 'Name'),
            ('location', 'Location'),
        ]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_warehouse'] = user_has_permission(self.request.user, 'add_warehouse')
        return context


@method_decorator(require_permission('add_warehouse'), name='dispatch')
class WarehouseCreateView(View):
    def get(self, request):
        context = {
            'warehouse': None,
            'name': '',
            'location': '',
        }
        return render(request, 'warehouse_form.html', context)

    def post(self, request):
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        if not name:
            context = {
                'error': 'Name required',
                'name': name,
                'location': location,
                'warehouse': None,
            }
            return render(request, 'warehouse_form.html', context)
        Warehouse.objects.create(name=name, location=location, company=request.user.company)
        return redirect('warehouse_list')


@method_decorator(require_permission('change_warehouse'), name='dispatch')
class WarehouseUpdateView(View):
    """Update an existing warehouse without using ModelForm."""

    def get_object(self, pk, user):
        return get_object_or_404(Warehouse, pk=pk, company=user.company)

    def get(self, request, pk):
        warehouse = self.get_object(pk, request.user)
        context = {
            'warehouse': warehouse,
            'name': warehouse.name,
            'location': warehouse.location,
        }
        return render(request, 'warehouse_form.html', context)

    def post(self, request, pk):
        warehouse = self.get_object(pk, request.user)
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        if not name:
            context = {
                'error': 'Name required',
                'warehouse': warehouse,
                'name': name,
                'location': location,
            }
            return render(request, 'warehouse_form.html', context)
        warehouse.name = name
        warehouse.location = location
        warehouse.save()
        return redirect('warehouse_list')


@method_decorator(require_permission('view_productcategory'), name='dispatch')
class ProductCategoryListView(AdvancedListMixin, TemplateView):
    template_name = 'category_list.html'
    model = ProductCategory
    search_fields = ['name']
    default_sort = 'name'

    def base_queryset(self):
        qs = ProductCategory.objects.filter(company=self.request.user.company)
        if self.request.GET.get('show') != 'all':
            qs = qs.filter(is_discontinued=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = []
        context['sort_options'] = [('name', 'Name')]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_category'] = user_has_permission(self.request.user, 'add_productcategory')
        return context


@method_decorator(require_permission('add_productcategory'), name='dispatch')
class ProductCategoryCreateView(View):
    def get(self, request):
        roots = ProductCategory.objects.filter(
            company=request.user.company, parent__isnull=True
        ).order_by('name')
        context = {
            'root_categories': roots,
            'category': None,
            'name': '',
            'parent': '',
        }
        return render(request, 'category_form.html', context)

    def post(self, request):
        name = request.POST.get('name', '').strip()
        parent_id = request.POST.get('parent')
        parent = None
        if parent_id and parent_id.isdigit():
            parent = get_object_or_404(ProductCategory, pk=parent_id, company=request.user.company)
        if not name:
            roots = ProductCategory.objects.filter(
                company=request.user.company, parent__isnull=True
            ).order_by('name')
            context = {
                'error': 'Name required',
                'root_categories': roots,
                'name': name,
                'parent': parent_id,
                'category': None,
            }
            return render(request, 'category_form.html', context)
        if ProductCategory.objects.filter(name=name, company=request.user.company).exists():
            roots = ProductCategory.objects.filter(
                company=request.user.company, parent__isnull=True
            ).order_by('name')
            context = {
                'error': 'Category with this name already exists',
                'root_categories': roots,
                'name': name,
                'parent': parent_id,
                'category': None,
            }
            return render(request, 'category_form.html', context)
        ProductCategory.objects.create(name=name, parent=parent, company=request.user.company)
        return redirect('category_add')


@method_decorator(require_permission('change_productcategory'), name='dispatch')
class ProductCategoryUpdateView(View):
    """Update a product category without ModelForms."""

    def get_object(self, pk, user):
        return get_object_or_404(ProductCategory, pk=pk, company=user.company)

    def get(self, request, pk):
        category = self.get_object(pk, request.user)
        roots = ProductCategory.objects.filter(
            company=request.user.company, parent__isnull=True
        ).exclude(pk=category.pk).order_by('name')
        context = {
            'category': category,
            'root_categories': roots,
            'name': category.name,
            'parent': category.parent_id,
        }
        return render(request, 'category_form.html', context)

    def post(self, request, pk):
        category = self.get_object(pk, request.user)
        name = request.POST.get('name', '').strip()
        parent_id = request.POST.get('parent')
        parent = None
        if parent_id and parent_id.isdigit():
            parent = get_object_or_404(ProductCategory, pk=parent_id, company=request.user.company)
        if not name:
            roots = ProductCategory.objects.filter(
                company=request.user.company, parent__isnull=True
            ).exclude(pk=category.pk).order_by('name')
            context = {
                'error': 'Name required',
                'category': category,
                'root_categories': roots,
                'name': name,
                'parent': parent_id,
            }
            return render(request, 'category_form.html', context)
        if ProductCategory.objects.filter(name=name, company=request.user.company).exclude(pk=category.pk).exists():
            roots = ProductCategory.objects.filter(
                company=request.user.company, parent__isnull=True
            ).exclude(pk=category.pk).order_by('name')
            context = {
                'error': 'Category with this name already exists',
                'category': category,
                'root_categories': roots,
                'name': name,
                'parent': parent_id,
            }
            return render(request, 'category_form.html', context)
        category.name = name
        category.parent = parent
        category.save()
        return redirect('category_list')




@require_permission('change_productcategory')
def category_rename(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk, company=request.user.company)
    if request.method == 'GET':
        return render(request, 'category_rename_form.html', {'category': category})
    name = request.POST.get('name', '').strip()
    if not name:
        return HttpResponseBadRequest('Name required')
    if ProductCategory.objects.filter(name=name, company=request.user.company).exclude(pk=category.pk).exists():
        return HttpResponseBadRequest('Category with this name already exists')
    category.name = name
    category.save()
    category.full_path_cached = category.full_path
    return render(request, 'includes/category_node.html', {'cat': category, 'editing': False})


@require_permission('change_productcategory')
def category_move(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk, company=request.user.company)
    parent_id = request.POST.get('parent')
    new_parent = None
    if parent_id:
        new_parent = get_object_or_404(ProductCategory, pk=parent_id, company=request.user.company)
        if category == new_parent or category.is_ancestor_of(new_parent):
            return HttpResponseBadRequest('Invalid parent')
    category.parent = new_parent
    category.save()
    return HttpResponse('OK')


def _discontinue_category(cat):
    """Recursively discontinue ``cat`` and cascade to products."""
    if cat.is_discontinued:
        return
    cat.is_discontinued = True
    cat.save(update_fields=['is_discontinued'])
    Product.objects.filter(category=cat).update(is_discontinued=True)
    for child in ProductCategory.objects.filter(parent=cat):
        _discontinue_category(child)


@require_permission('discontinue_productcategory')
def category_discontinue(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk, company=request.user.company)
    if request.method == 'POST':
        _discontinue_category(category)
        return HttpResponse('OK')
    return HttpResponseBadRequest('Invalid request')


@require_permission('view_productcategory')
def category_children(request):
    """Return child categories as JSON for AJAX cascading selects."""
    parent_id = request.GET.get('parent_id') or request.GET.get('parent')  # accept both keys
    level = int(request.GET.get('level', 1))
    parent = None
    if parent_id and str(parent_id).isdigit():
        parent = get_object_or_404(ProductCategory, pk=parent_id, company=request.user.company)
    elif parent_id:  # something invalid
        return JsonResponse([], safe=False)
    cats = ProductCategory.objects.filter(parent=parent, company=request.user.company).order_by('name')
    if request.GET.get('show') != 'all':
        cats = cats.filter(is_discontinued=False)
    data = []
    for c in cats:
        has_children = ProductCategory.objects.filter(parent=c, is_discontinued=False).exists()
        data.append({'id': c.id, 'name': c.name, 'has_children': has_children, 'is_discontinued': c.is_discontinued})
    return JsonResponse(data, safe=False)


@require_permission('add_productcategory')
def category_quick_add(request):
    """Create a category via HTMX and return an option element."""
    name = request.POST.get('name', '').strip()
    if not name:
        return HttpResponseBadRequest('Name required')
    if ProductCategory.objects.filter(name=name, company=request.user.company).exists():
        return HttpResponseBadRequest('Category with this name already exists')
    parent_id = request.POST.get('parent')
    parent = None
    if parent_id and parent_id.isdigit():
        parent = get_object_or_404(ProductCategory, pk=parent_id, company=request.user.company)
    category = ProductCategory.objects.create(name=name, parent=parent, company=request.user.company)
    return render(request, 'includes/category_option.html', {'category': category}, status=201)


@require_permission('add_productunit')
def unit_quick_add(request):
    """Create a unit via AJAX and return an option element."""
    code = request.POST.get('code', '').strip()
    name = request.POST.get('name', '').strip()
    if not code or not name:
        return HttpResponseBadRequest('All fields required')
    if ProductUnit.objects.filter(code__iexact=code).exists() or ProductUnit.objects.filter(name__iexact=name).exists():
        return HttpResponseBadRequest('Unit exists')
    unit = ProductUnit.objects.create(code=code, name=name)
    log_action(request.user, 'create_unit', details={'code': code})
    return render(request, 'includes/unit_option.html', {'unit': unit}, status=201)




@method_decorator(require_permission('view_product'), name='dispatch')
class ProductListView(AdvancedListMixin, TemplateView):
    template_name = 'product_list.html'
    model = Product
    search_fields = ['name', 'sku', 'brand']
    default_sort = 'name'

    def base_queryset(self):
        qs = Product.objects.filter(company=self.request.user.company)
        if self.request.GET.get('show') != 'all':
            qs = qs.filter(is_discontinued=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = []
        context['sort_options'] = [('name', 'Name'), ('sku', 'SKU')]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_product'] = user_has_permission(self.request.user, 'add_product')
        return context


@method_decorator(require_permission('add_product'), name='dispatch')
class ProductCreateView(View):
    def get(self, request):
        units = ProductUnit.objects.all()
        can_add_productunit = user_has_permission(request.user, 'add_productunit')
        return render(
            request, 
            'product_form.html', 
            {
                'units': units,
                'can_add_productunit': can_add_productunit,
            }
            )

    def post(self, request):
        name = request.POST.get('name', '').strip()
        sku = request.POST.get('sku', '').strip()
        unit_id = request.POST.get('unit')
        unit = get_object_or_404(ProductUnit, pk=unit_id) if unit_id else None
        if not name or not sku or not unit:
            units = ProductUnit.objects.all()
            return render(request, 'product_form.html', {'error': 'All fields required', 'units': units})
        brand = request.POST.get('brand', '').strip()
        cat_id = request.POST.get('category')
        category = None
        if cat_id:
            category = get_object_or_404(ProductCategory, pk=cat_id, company=request.user.company)
            if ProductCategory.objects.filter(parent=category).exists():
                units = ProductUnit.objects.all()
                err = 'Category must be a leaf node'
                return render(request, 'product_form.html', {'error': err, 'units': units})
        Product.objects.create(
            name=name,
            sku=sku,
            unit=unit,
            brand=brand,
            category=category,
            company=request.user.company,
            barcode=request.POST.get('barcode', '').strip(),
            description=request.POST.get('description', '').strip()
        )
        log_action(request.user, 'create_product', details={'sku': sku}, company=request.user.company)
        return redirect('product_list')


@method_decorator(require_permission('view_stocklot'), name='dispatch')
class StockLotListView(AdvancedListMixin, TemplateView):
    template_name = 'stock_lot_list.html'
    model = StockLot
    search_fields = ['batch_number']
    default_sort = 'batch_number'

    def base_queryset(self):
        return StockLot.objects.filter(product__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = []
        context['sort_options'] = [('batch_number', 'Batch')]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_stocklot'] = user_has_permission(self.request.user, 'add_stocklot')
        return context


@method_decorator(require_permission('add_stocklot'), name='dispatch')
class StockLotCreateView(View):
    def get(self, request):
        products = Product.objects.filter(company=request.user.company)
        warehouses = Warehouse.objects.filter(company=request.user.company)
        return render(request, 'stock_lot_form.html', {'products': products, 'warehouses': warehouses})

    def post(self, request):
        product = get_object_or_404(Product, pk=request.POST.get('product'), company=request.user.company)
        warehouse = get_object_or_404(Warehouse, pk=request.POST.get('warehouse'), company=request.user.company)
        batch_number = request.POST.get('batch_number', '').strip()
        qty = request.POST.get('qty', '0').strip()
        if not batch_number or qty == '':
            products = Product.objects.filter(company=request.user.company)
            warehouses = Warehouse.objects.filter(company=request.user.company)
            return render(request, 'stock_lot_form.html', {'error': 'All fields required', 'products': products, 'warehouses': warehouses})
        StockLot.objects.create(
            product=product,
            warehouse=warehouse,
            batch_number=batch_number,
            expiry_date=request.POST.get('expiry_date') or None,
            qty=qty
        )
        log_action(request.user, 'create_lot', company=request.user.company)
        return redirect('stock_lot_list')


@method_decorator(require_permission('view_stockmovement'), name='dispatch')
class StockMovementListView(AdvancedListMixin, TemplateView):
    template_name = 'stock_movement_list.html'
    model = StockMovement
    search_fields = ['reference']
    default_sort = '-date'

    def base_queryset(self):
        return StockMovement.objects.filter(product__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = True
        context['filters'] = []
        context['sort_options'] = [('date', 'Date')]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_stockmovement'] = user_has_permission(self.request.user, 'add_stockmovement')
        return context


@method_decorator(require_permission('add_stockmovement'), name='dispatch')
class StockMovementCreateView(View):
    def get(self, request):
        products = Product.objects.filter(company=request.user.company)
        warehouses = Warehouse.objects.filter(company=request.user.company)
        return render(request, 'stock_movement_form.html', {
            'products': products,
            'warehouses': warehouses
        })

    def post(self, request):
        product = get_object_or_404(Product, pk=request.POST.get('product'), company=request.user.company)
        warehouse = get_object_or_404(Warehouse, pk=request.POST.get('warehouse'), company=request.user.company)
        qty = request.POST.get('qty', '0').strip()
        mtype = request.POST.get('movement_type')
        if qty == '' or mtype not in [StockMovement.IN, StockMovement.OUT, StockMovement.TRANSFER]:
            products = Product.objects.filter(company=request.user.company)
            warehouses = Warehouse.objects.filter(company=request.user.company)
            return render(request, 'stock_movement_form.html', {
                'error': 'All fields required',
                'products': products,
                'warehouses': warehouses
            })
        StockMovement.objects.create(
            product=product,
            warehouse=warehouse,
            quantity=qty,
            movement_type=mtype,
            user=request.user,
            reference=request.POST.get('reference', '').strip()
        )
        log_action(request.user, 'stock_move', company=request.user.company)
        return redirect('stock_movement_list')


@method_decorator(require_permission('view_inventoryadjustment'), name='dispatch')
class InventoryAdjustmentListView(AdvancedListMixin, TemplateView):
    template_name = 'inventory_adjustment_list.html'
    model = InventoryAdjustment
    search_fields = []
    default_sort = '-date'

    def base_queryset(self):
        return InventoryAdjustment.objects.filter(product__company=self.request.user.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_queryset()
        context['page_obj'] = page
        context['search'] = False
        context['filters'] = []
        context['sort_options'] = [('date', 'Date')]
        context['query_string'] = self.query_string()
        context['sort_query_string'] = self.sort_query_string()
        context['can_add_inventoryadjustment'] = user_has_permission(self.request.user, 'add_inventoryadjustment')
        return context


@method_decorator(require_permission('add_inventoryadjustment'), name='dispatch')
class InventoryAdjustmentCreateView(View):
    def get(self, request):
        products = Product.objects.filter(company=request.user.company)
        warehouses = Warehouse.objects.filter(company=request.user.company)
        return render(request, 'inventory_adjustment_form.html', {
            'products': products,
            'warehouses': warehouses,
            'choices': InventoryAdjustment.REASON_CHOICES,
        })

    def post(self, request):
        product = get_object_or_404(Product, pk=request.POST.get('product'), company=request.user.company)
        warehouse = get_object_or_404(Warehouse, pk=request.POST.get('warehouse'), company=request.user.company)
        qty = request.POST.get('qty', '0').strip()
        reason = request.POST.get('reason')
        if qty == '' or reason not in dict(InventoryAdjustment.REASON_CHOICES):
            products = Product.objects.filter(company=request.user.company)
            warehouses = Warehouse.objects.filter(company=request.user.company)
            return render(request, 'inventory_adjustment_form.html', {
                'error': 'All fields required',
                'products': products,
                'warehouses': warehouses,
                'choices': InventoryAdjustment.REASON_CHOICES,
            })
        InventoryAdjustment.objects.create(
            product=product,
            warehouse=warehouse,
            qty=qty,
            reason=reason,
            notes=request.POST.get('notes', ''),
            user=request.user
        )
        log_action(request.user, 'inventory_adjust', company=request.user.company)
        return redirect('inventory_adjustment_list')


@require_permission('view_stock_on_hand')
def stock_on_hand(request):
    products = Product.objects.filter(company=request.user.company)
    data = []
    for prod in products:
        qty_lots = StockLot.objects.filter(product=prod).aggregate(q=Sum('qty'))['q'] or 0
        qty_moves_in = StockMovement.objects.filter(product=prod, movement_type=StockMovement.IN).aggregate(q=Sum('quantity'))['q'] or 0
        qty_moves_out = StockMovement.objects.filter(product=prod, movement_type=StockMovement.OUT).aggregate(q=Sum('quantity'))['q'] or 0
        qty_adj = InventoryAdjustment.objects.filter(product=prod).aggregate(q=Sum('qty'))['q'] or 0
        total = qty_lots + qty_moves_in - qty_moves_out + qty_adj
        data.append({'product': prod, 'qty': total})
    return render(request, 'stock_on_hand.html', {'data': data})
