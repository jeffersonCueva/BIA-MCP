from fastmcp import FastMCP
from app.services.backend_service import get_bank_account_number
from app.services.bank_service import get_transactions


def register(mcp: FastMCP):

    @mcp.tool()
    def fetch_transactions(bank: str):
        """
        Get transaction history for a user from a specific bank.
        """
        account = get_bank_account_number(bank)
        return get_transactions(bank, account)
