from fastmcp import FastMCP
from app.services.backend_service import get_logged_in_user, get_bank_account_number


def register(mcp: FastMCP):

    @mcp.tool()
    def fetch_logged_in_user() -> object:
        """
        Get the details of the logged in user
        """
        return get_logged_in_user()

    @mcp.tool()
    def fetch_bank_account_number(bank: str) -> str:
        """
        get the account number of specific bank of the logged in user
        """
        account_number = get_bank_account_number(bank)
        if isinstance(account_number, dict) and account_number.get("status") == "error":
            return account_number
        if not account_number:
            return (
                "Could not resolve your bank account number from backend. "
                "Account-dependent operations require BIABACKENDURL to be reachable."
            )
        return account_number
