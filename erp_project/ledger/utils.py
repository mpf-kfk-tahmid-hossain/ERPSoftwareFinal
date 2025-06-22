from decimal import Decimal
from django.db.models import Sum
from .models import LedgerEntry, LedgerLine, LedgerAccount


def post_entry(company, description, lines, ensure_funds=True):
    """Create a ledger entry with given lines and optional balance checks."""

    entry = LedgerEntry.objects.create(company=company, description=description)
    for code, debit, credit in lines:
        account = LedgerAccount.objects.get(code=code, company=company)
        LedgerLine.objects.create(
            entry=entry,
            account=account,
            debit=Decimal(debit),
            credit=Decimal(credit),
        )

    if ensure_funds:
        for code in ["Cash", "Bank"]:
            account = LedgerAccount.objects.filter(code=code, company=company).first()
            if not account:
                continue
            bal = (
                LedgerLine.objects.filter(account=account, entry__company=company)
                .aggregate(total=Sum("debit") - Sum("credit"))
                ["total"]
                or Decimal("0")
            )
            if bal < 0:
                raise ValueError(f"{code} balance negative")

    return entry
