import httpx
import logging
from app.config import BANK_APIS, CLEARING_HOUSE_API


def same_bank_transfer(from_bank, from_account, to_account, amount):
    api = BANK_APIS.get(from_bank.lower())
    if not api:
        return "Unknown bank."

    payload = {
        "from_account": from_account,
        "to_account": to_account,
        "from_bank": from_bank,
        "to_bank": from_bank,
        "amount": amount,
    }

    try:
        response = httpx.post(f"{api}/transfer", json=payload, timeout=5)
        response.raise_for_status()
        return response.json().get("message", "Transfer successful.")
    except httpx.HTTPError as e:
        logging.error(e)
        return "Transfer failed."


def interbank_transfer(from_bank, from_account, to_bank, to_account, amount):
    payload = {
        "from_bank": from_bank,
        "from_account": from_account,
        "to_bank": to_bank,
        "to_account": to_account,
        "amount": amount,
    }

    try:
        response = httpx.post(
            f"{CLEARING_HOUSE_API}/interbank-transfer",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get(
            "message", "Interbank transfer completed successfully."
        )
    except httpx.HTTPError as e:
        logging.error(e)
        return "Interbank transfer failed."
