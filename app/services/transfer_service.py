import httpx
import logging
from app.config import BANK_APIS, CLEARING_HOUSE_API
from app.services.bank_service import format_bank_account_id


def same_bank_transfer(from_bank, from_account, to_account, amount):
    api = BANK_APIS.get(from_bank.lower())
    if not api:
        return "Unknown bank."

    from_account_id = format_bank_account_id(from_bank, from_account)
    to_account_id = format_bank_account_id(from_bank, to_account)

    payload = {
        "from_account": from_account_id,
        "to_account": to_account_id,
        "from_bank": from_bank.upper(),
        "to_bank": from_bank.upper(),
        "amount": amount,
    }

    try:
        response = httpx.post(f"{api}/transfer", json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return data
        return "Transfer successful."
    except httpx.HTTPError as e:
        logging.error(e)
        return "Transfer failed."


def interbank_transfer(from_bank, from_account, to_bank, to_account, amount):
    from_api = BANK_APIS.get(from_bank.lower())
    to_api = BANK_APIS.get(to_bank.lower())
    if not from_api:
        return "Unknown source bank."
    if not to_api:
        return "Unknown destination bank."

    from_account_id = format_bank_account_id(from_bank, from_account)
    to_account_id = format_bank_account_id(to_bank, to_account)

    payload = {
        "from_bank": from_bank.upper(),
        "from_account": from_account_id,
        "to_bank": to_bank.upper(),
        "to_account": to_account_id,
        "amount": amount,
    }

    try:
        response = httpx.post(
            f"{CLEARING_HOUSE_API}/interbank-transfer",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return data
        return "Interbank transfer completed successfully."
    except httpx.HTTPError as e:
        logging.error(e)
        return "Interbank transfer failed."
