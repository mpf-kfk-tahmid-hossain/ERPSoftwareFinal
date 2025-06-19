from django import template
from accounts.utils import user_has_permission

register = template.Library()


@register.filter
def has_permission(user, codename):
    """Template filter to check a user's permission."""
    return user_has_permission(user, codename)
