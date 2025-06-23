from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from erp_project.accounts.utils import require_permission
from erp_project.inventory.models import Product, ProductSerial


@login_required
@require_permission('view_product')
def pos_scan(request):
    """Scan EAN or serial to identify a product."""
    context = {}
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        product = None
        if Product.objects.filter(barcode=code, company=request.user.company).exists():
            product = Product.objects.get(barcode=code, company=request.user.company)
        else:
            serial_obj = ProductSerial.objects.filter(serial=code, product__company=request.user.company).first()
            if serial_obj:
                product = serial_obj.product
        if product:
            context['product'] = product
        else:
            context['error'] = 'Not found'
    return render(request, 'pos_scan.html', context)
