import httpx
import logging
from app.config import BIA_BACKEND, LOGGED_IN_USER


def get_logged_in_user():
    try:
        response = httpx.get(
            f"{BIA_BACKEND}/accounts/{LOGGED_IN_USER}",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logging.error(e)
        return None


def get_bank_account_number(bank: str):
    try:
        response = httpx.get(
            f"{BIA_BACKEND}/accounts/bank/{LOGGED_IN_USER}/{bank}",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        logging.error(e)
        return None
