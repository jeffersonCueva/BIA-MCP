import httpx
import logging
from app.config import BANK_APIS

logger = logging.getLogger(__name__)


def format_bank_account_id(bank: str, account: str) -> str:
    """
    Convert backend account values to bank endpoint account IDs.
    Example: bank='bpi', account='2000000001' -> 'BPI001'
    """
    bank_prefix = "".join(ch for ch in str(bank).upper() if ch.isalnum())
    raw_account = str(account or "").strip()
    if not bank_prefix or not raw_account:
        return raw_account

    normalized = raw_account.upper()
    if normalized.startswith(bank_prefix):
        return normalized

    digits = "".join(ch for ch in raw_account if ch.isdigit())
    suffix = digits[-3:] if len(digits) >= 3 else raw_account[-3:]
    return f"{bank_prefix}{suffix}"


def get_balance(bank: str, account: str):
    api = BANK_APIS.get(bank.lower())
    if not api:
        return {
            "status": "error",
            "message": f"Unknown bank: {bank}",
            "bank": bank,
            "account": account,
        }

    formatted_account = format_bank_account_id(bank, account)

    try:
        url = f"{api}/balance/{formatted_account}"
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            return {
                "status": "error",
                "message": "Unexpected balance response format",
                "bank": bank,
                "account": formatted_account,
                "url": url,
                "response": data,
            }

        if "balance" not in data:
            return {
                "status": "error",
                "message": "Balance key missing in response",
                "bank": bank,
                "account": formatted_account,
                "url": url,
                "response": data,
            }

        return data["balance"]
    except httpx.HTTPStatusError as e:
        logger.error("Balance lookup failed: %s", e)
        return {
            "status": "error",
            "message": "Bank API returned non-success status",
            "bank": bank,
            "account": formatted_account,
            "url": str(e.request.url),
            "status_code": e.response.status_code,
            "response": e.response.text,
        }
    except httpx.HTTPError as e:
        logger.error("Balance lookup failed: %s", e)
        return {
            "status": "error",
            "message": "Failed to call bank balance endpoint",
            "bank": bank,
            "account": formatted_account,
            "url": f"{api}/balance/{formatted_account}",
            "error": str(e),
        }


def get_transactions(bank: str, account: str):
    api = BANK_APIS.get(bank.lower())
    if not api:
        return []

    formatted_account = format_bank_account_id(bank, account)

    try:
        response = httpx.get(f"{api}/transactions/{formatted_account}", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("transactions", data)
    except httpx.HTTPError as e:
        logging.error(e)
        return []


def fetch_billers_for_bank(bank: str):
    api = BANK_APIS.get(bank.lower())
    if not api:
        return {}

    try:
        response = httpx.get(f"{api}/supported-billers", timeout=5)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, dict):
            return {k.strip().upper(): v for k, v in data.items()}

        if isinstance(data, list):
            billers = {}
            for item in data:
                if isinstance(item, dict):
                    code = item.get("code", "").upper()
                    name = item.get("name", "")
                    if code:
                        billers[code] = name
                else:
                    billers[str(item).upper()] = str(item)
            return billers

        return {}

    except httpx.HTTPError as e:
        logging.error(e)
        return {}
