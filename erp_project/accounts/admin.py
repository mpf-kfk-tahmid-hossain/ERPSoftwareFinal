from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *

admin.site.register(Company)
admin.site.register(Role)
admin.site.register(UserRole)

@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    # Show company in list view
    list_display = DjangoUserAdmin.list_display + ('company',)
    list_filter = DjangoUserAdmin.list_filter + ('company',)

    # Add 'company' to fieldsets for editing existing users
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Company Info', {'fields': ('company',)}),
    )

    # Add 'company' to fieldsets for creating new users
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Company Info', {'fields': ('company',)}),
    )

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'description')
    search_fields = ('codename', 'description')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    list_filter = ('role', 'permission')
    search_fields = ('role__name', 'permission__codename')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'actor',
        'action',
        'request_type',
        'target_user',
        'company',
    )
    list_filter = ('request_type', 'action', 'company', 'actor')
    search_fields = (
        'actor__username',
        'target_user__username',
        'action',
        'details',
    )

