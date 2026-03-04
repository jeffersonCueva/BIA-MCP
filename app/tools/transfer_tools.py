from fastmcp import FastMCP
from app.services.backend_service import get_bank_account_number
from app.services.transfer_service import (
    same_bank_transfer,
    interbank_transfer,
)


def register(mcp: FastMCP):

    @mcp.tool()
    def transfer_funds(
        to_account_number: str,
        to_bank: str,
        amount: int,
        from_bank: str = None,
    ):
        """
        Transfer funds using bank transfer rails.

        Transfer intent rules:
        - Same-bank transfer: if from_bank == to_bank, this uses the bank /transfer endpoint.
        - Interbank transfer: if from_bank != to_bank, this uses clearing-house /interbank-transfer.

        Input guidance:
        - Use bank codes: BPI or GCASH.
        - Provide to_account_number as the destination account id/value.
        - Provide amount as a positive integer.
        - from_bank is optional; if omitted, user is prompted.

        Notes:
        - Account ids are normalized by service logic to bank format (e.g., BPI001, GCASH001).
        - Returns API response payloads from transfer endpoints.
        """
        if not from_bank:
            from_bank = mcp.ask("Please enter your bank name:")

        from_account = get_bank_account_number(from_bank)
        if isinstance(from_account, dict) and from_account.get("status") == "error":
            return from_account
        if not from_account:
            return (
                "Could not resolve your source account number from backend. "
                "Transfers require BIABACKENDURL to be reachable."
            )

        if from_bank.lower() == to_bank.lower():
            return same_bank_transfer(
                from_bank,
                from_account,
                to_account_number,
                amount,
            )

        return interbank_transfer(
            from_bank,
            from_account,
            to_bank,
            to_account_number,
            amount,
        )
