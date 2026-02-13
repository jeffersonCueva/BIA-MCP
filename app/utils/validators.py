import re

def valid_email(email: str) -> bool:
    """
    Validates standard email format.
    """
    if not email:
        return False
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


def valid_mobile(mobile: str) -> bool:
    """
    Validates PH-style mobile numbers:
    - 10 to 13 digits
    - digits only
    """
    if not mobile:
        return False
    return bool(re.match(r"^\d{10,13}$", mobile))
