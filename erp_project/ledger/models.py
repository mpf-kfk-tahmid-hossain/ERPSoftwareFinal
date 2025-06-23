from django.db import models
from erp_project.accounts.models import Company


class LedgerAccount(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('code', 'company')

    def __str__(self):
        return f"{self.code} - {self.name}"


class LedgerEntry(models.Model):
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.date} {self.description}"


class LedgerLine(models.Model):
    entry = models.ForeignKey(LedgerEntry, related_name='lines', on_delete=models.CASCADE)
    account = models.ForeignKey(LedgerAccount, on_delete=models.PROTECT)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)

