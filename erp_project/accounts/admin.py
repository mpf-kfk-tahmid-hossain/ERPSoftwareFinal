from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import *

admin.site.register(Company)
admin.site.register(Role)
admin.site.register(User, DjangoUserAdmin)
admin.site.register(UserRole)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'description')
    search_fields = ('codename', 'description')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    list_filter = ('role', 'permission')
    search_fields = ('role__name', 'permission__codename')

admin.site.register(AuditLog)

