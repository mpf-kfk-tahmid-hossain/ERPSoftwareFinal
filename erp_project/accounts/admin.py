from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Company, Role, User, UserRole

admin.site.register(Company)
admin.site.register(Role)
admin.site.register(User, DjangoUserAdmin)
admin.site.register(UserRole)
