import httpx
import logging
from app.config import (
    BIA_BACKEND,
    DEMO_BANK_ACCOUNT_IDS,
    LOGGED_IN_USER,
    LOCAL_USER_PROFILE,
    USE_DEMO_BANK_ACCOUNT_IDS,
    USE_LOCAL_USER_FALLBACK,
)

logger = logging.getLogger(__name__)


def _has_logged_in_user() -> bool:
    return bool(LOGGED_IN_USER and LOGGED_IN_USER.lower() != "none")


def get_logged_in_user():
    if not _has_logged_in_user():
        logger.error("LOGGED_IN_USER is not set")
        return {
            "status": "error",
            "message": "LOGGED_IN_USER is not configured",
        }

    try:
        response = httpx.get(
            f"{BIA_BACKEND}/account/{LOGGED_IN_USER}",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        logger.error("Failed to fetch logged-in user: %s", e)
        if USE_LOCAL_USER_FALLBACK:
            return LOCAL_USER_PROFILE
        return {
            "status": "error",
            "message": "Backend returned non-success status for logged-in user lookup",
            "user_id": LOGGED_IN_USER,
            "url": str(e.request.url),
            "status_code": e.response.status_code,
            "response": e.response.text,
        }
    except httpx.HTTPError as e:
        logger.error("Failed to fetch logged-in user: %s", e)
        if USE_LOCAL_USER_FALLBACK:
            return LOCAL_USER_PROFILE
        return {
            "status": "error",
            "message": "Failed to call backend for logged-in user lookup",
            "user_id": LOGGED_IN_USER,
            "url": f"{BIA_BACKEND}/account/{LOGGED_IN_USER}",
            "error": str(e),
        }


def get_bank_account_number(bank: str):
    if not _has_logged_in_user():
        logger.error("LOGGED_IN_USER is not set")
        return {
            "status": "error",
            "message": "LOGGED_IN_USER is not configured",
        }

    bank_value = (bank or "").strip().lower()
    if not bank_value:
        return {
            "status": "error",
            "message": "Bank is required",
        }

    # Demo mode: bypass backend lookup and use normalized account IDs directly.
    if USE_DEMO_BANK_ACCOUNT_IDS:
        demo_account_id = DEMO_BANK_ACCOUNT_IDS.get(bank_value)
        if demo_account_id:
            return demo_account_id

    url = f"{BIA_BACKEND}/account/bank/{LOGGED_IN_USER}/{bank_value}"

    try:
        response = httpx.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            for key in ("account_number", "accountNumber", "account"):
                if data.get(key):
                    return data[key]
        return {
            "status": "error",
            "message": "Account number key missing in backend response",
            "bank": bank_value,
            "url": url,
            "response": data,
        }
    except httpx.HTTPStatusError as e:
        logger.error("Failed to fetch bank account number: %s", e)
        return {
            "status": "error",
            "message": "Backend returned non-success status for bank account lookup",
            "bank": bank_value,
            "user_id": LOGGED_IN_USER,
            "url": str(e.request.url),
            "status_code": e.response.status_code,
            "response": e.response.text,
        }
    except httpx.HTTPError as e:
        logger.error("Failed to fetch bank account number: %s", e)
        return {
            "status": "error",
            "message": "Failed to call backend for bank account lookup",
            "bank": bank_value,
            "user_id": LOGGED_IN_USER,
            "url": url,
            "error": str(e),
        }
