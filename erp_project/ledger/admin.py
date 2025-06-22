from django.contrib import admin
from .models import LedgerAccount, LedgerEntry, LedgerLine

admin.site.register(LedgerAccount)
admin.site.register(LedgerEntry)
admin.site.register(LedgerLine)
