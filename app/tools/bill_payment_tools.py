from fastmcp import FastMCP
from app.services.bank_service import fetch_billers_for_bank, format_bank_account_id
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
        bank_value = (bank or "").strip().lower()
        if not bank_value:
            return {"status": "error", "message": "Bank is required"}

        if not isinstance(amount, int) or amount <= 0:
            return {"status": "error", "message": "Amount must be a positive integer"}

        account = get_bank_account_number(bank_value)
        if isinstance(account, dict) and account.get("status") == "error":
            return account
        if not account:
            return (
                "Could not resolve your bank account number from backend. "
                "Bill payment requires BIABACKENDURL to be reachable."
            )

        # Keep bill-payment account IDs aligned with balance/transactions endpoint format.
        formatted_account = format_bank_account_id(bank_value, account)

        api = BANK_APIS.get(bank_value)
        if not api:
            return f"Unknown bank: {bank}"

        billers = fetch_billers_for_bank(bank_value)
        if not billers:
            return {
                "status": "error",
                "message": "Could not load supported billers for bank",
                "bank": bank_value,
            }

        biller_code = biller_code.upper()

        if biller_code not in billers:
            return f"Unsupported biller code. Supported: {list(billers.keys())}"

        payload = {
            "account_holder": formatted_account,
            "biller_code": biller_code,
            "reference_number": reference_number,
            "amount": amount,
        }

        try:
            url = f"{api}/bill-payment"
            response = httpx.post(
                url,
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data
            return {
                "status": "error",
                "message": "Unexpected bill-payment response format",
                "bank": bank_value,
                "url": url,
                "response": data,
            }
        except httpx.HTTPStatusError as e:
            logging.error(e)
            return {
                "status": "error",
                "message": "Bank API returned non-success status for bill payment",
                "bank": bank_value,
                "account": formatted_account,
                "url": str(e.request.url),
                "status_code": e.response.status_code,
                "response": e.response.text,
                "payload": payload,
            }
        except httpx.HTTPError as e:
            logging.error(e)
            return {
                "status": "error",
                "message": "Failed to call bank bill-payment endpoint",
                "bank": bank_value,
                "account": formatted_account,
                "url": f"{api}/bill-payment",
                "error": str(e),
                "payload": payload,
            }
