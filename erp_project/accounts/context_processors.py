from types import SimpleNamespace
from .utils import user_has_permission


def nav_permissions(request):
    """Return permission flags for navigation menu items."""
    if not request.user.is_authenticated or not getattr(request.user, 'company', None):
        return {}
    codes = [
        'view_user',
        'view_role',
        'view_warehouse',
        'view_productcategory',
        'view_product',
        'view_supplier',
        'add_quotationrequest',
        'add_purchaseorder',
        'view_stocklot',
        'view_stockmovement',
        'view_inventoryadjustment',
        'view_stock_on_hand',
        'view_auditlog',
    ]
    perms = {code: user_has_permission(request.user, code) for code in codes}
    return {'nav_perms': SimpleNamespace(**perms)}

