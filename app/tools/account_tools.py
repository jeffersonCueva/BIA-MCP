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
        return get_bank_account_number(bank)
