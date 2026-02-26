from fastmcp import FastMCP
from app.services.backend_service import get_bank_account_number
from app.services.bank_service import get_balance


def register(mcp: FastMCP):

    @mcp.tool()
    def fetch_balance(bank: str):
        """
        Get the balance of a user from a specific bank.
        """

        account = get_bank_account_number(bank)
        if isinstance(account, dict) and account.get("status") == "error":
            return account
        if not account:
            return {
                "status": "error",
                "message": (
                    "Could not resolve your bank account number from backend. "
                    "Balance lookup requires BIABACKENDURL to be reachable."
                ),
                "bank": bank,
            }
        return get_balance(bank, account)
