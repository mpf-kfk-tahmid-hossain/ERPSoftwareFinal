import re
import phonenumbers
from stdnum import iban as stdnum_iban


def validate_phone(value: str) -> bool:
    """Return True if value is a valid phone number."""
    try:
        num = phonenumbers.parse(value, None)
        return phonenumbers.is_valid_number(num)
    except phonenumbers.NumberParseException:
        return False


def validate_trade_license(value: str) -> bool:
    """Alphanumeric and dashes, 3-50 chars."""
    return bool(re.fullmatch(r"[A-Za-z0-9-]{3,50}", value))


def validate_trn(value: str) -> bool:
    """Digits only, 15 characters."""
    return bool(re.fullmatch(r"\d{15}", value))


def validate_iban(value: str) -> bool:
    """Validate IBAN using stdnum library."""
    try:
        return stdnum_iban.is_valid(value)
    except Exception:
        return False


def validate_swift(value: str) -> bool:
    """SWIFT codes are 8 or 11 uppercase letters/digits."""
    return bool(re.fullmatch(r"[A-Z0-9]{8}([A-Z0-9]{3})?", value))
