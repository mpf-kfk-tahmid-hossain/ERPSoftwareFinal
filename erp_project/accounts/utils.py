from functools import wraps
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Permission


def require_permission(codename=None, allow_self=False):
    """Decorator enforcing a custom permission. Superusers bypass checks.

    If ``allow_self`` is True, the view is allowed when the target ``pk`` in the
    URL matches the logged-in user's id.
    ``codename`` is auto-created if missing.
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if allow_self:
                target_pk = kwargs.get("pk")
                if target_pk and int(target_pk) == request.user.pk:
                    return view_func(request, *args, **kwargs)

            if codename:
                perm_obj, _ = Permission.objects.get_or_create(
                    codename=codename,
                    defaults={"description": codename},
                )
                has_perm = request.user.userrole_set.filter(
                    role__permissions=perm_obj,
                    company=request.user.company,
                ).exists()
                if has_perm:
                    return view_func(request, *args, **kwargs)
                return render(
                    request,
                    "403.html",
                    {"missing_permission": codename},
                    status=403,
                )
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def user_has_permission(user, codename):
    """Check if ``user`` has the custom permission ``codename``."""
    if user.is_superuser:
        return True
    try:
        perm = Permission.objects.get(codename=codename)
    except Permission.DoesNotExist:
        return False
    return user.userrole_set.filter(role__permissions=perm, company=user.company).exists()


def log_action(actor, action, target=None, details="", request_type=None, company=None):
    """Create an AuditLog entry.

    ``details`` can be a dictionary which will be stored as JSON.
    """
    from .models import AuditLog
    if isinstance(details, dict):
        details = json.dumps(details)
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target_user=target,
        details=details,
        request_type=request_type,
        company=company or getattr(actor, "company", None),
    )

