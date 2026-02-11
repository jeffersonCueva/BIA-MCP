from fastmcp import FastMCP
from app.services.bank_service import fetch_billers_for_bank
from app.services.backend_service import get_bank_account_number

import httpx
import logging
from app.config import BANK_APIS


def register(mcp: FastMCP):

    @mcp.tool()
    def get_billers_for_bank(bank: str):
        """
        get the list of billers that the bank accepts
        """
        return fetch_billers_for_bank(bank)

    @mcp.tool()
    def pay_bill(
        bank: str,
        biller_code: str,
        reference_number: str,
        amount: int,
    ):
        """
        pay a bill using the specified bank, reference number and amount
        """
        user = get_bank_account_number(bank)
        api = BANK_APIS.get(bank.lower())
        if not api:
            return f"Unknown bank: {bank}"

        billers = fetch_billers_for_bank(bank)
        biller_code = biller_code.upper()

        if biller_code not in billers:
            return f"Unsupported biller code. Supported: {list(billers.keys())}"

        payload = {
            "account_holder": user,
            "biller_code": biller_code,
            "reference_number": reference_number,
            "amount": amount,
        }

        try:
            response = httpx.post(
                f"{api}/bill-payment",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            return response.json().get(
                "message", "Bill payment completed successfully."
            )
        except httpx.HTTPError as e:
            logging.error(e)
            return "Bill payment failed."
