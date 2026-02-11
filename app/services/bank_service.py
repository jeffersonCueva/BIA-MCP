import httpx
import logging
from app.config import BANK_APIS


def get_balance(bank: str, account: str):
    api = BANK_APIS.get(bank.lower())
    if not api:
        return 0

    try:
        response = httpx.get(f"{api}/balance/{account}", timeout=5)
        response.raise_for_status()
        return response.json().get("balance", 0)
    except httpx.HTTPError as e:
        logging.error(e)
        return 0


def get_transactions(bank: str, account: str):
    api = BANK_APIS.get(bank.lower())
    if not api:
        return []

    try:
        response = httpx.get(f"{api}/transactions/{account}", timeout=5)
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
