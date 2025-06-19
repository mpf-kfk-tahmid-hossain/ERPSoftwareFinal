from django.contrib import admin
from .models import Company, Role, User, UserRole

admin.site.register(Company)
admin.site.register(Role)
admin.site.register(User)
admin.site.register(UserRole)
