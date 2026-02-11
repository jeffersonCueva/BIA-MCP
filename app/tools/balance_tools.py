from fastmcp import FastMCP
from app.services.backend_service import get_bank_account_number
from app.services.bank_service import get_balance


def register(mcp: FastMCP):

    @mcp.tool()
    def fetch_balance(bank: str) -> int:
        """
        Get the balance of a user from a specific bank.
        """

        account = get_bank_account_number(bank)
        return get_balance(bank, account)
