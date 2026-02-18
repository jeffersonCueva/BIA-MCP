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
        Transfer funds between users. for the to_account_number, always use the account number
        Elicits source bank and account only if not provided.
        Supports same-bank and interbank transfers.
        """
        if not from_bank:
            from_bank = mcp.ask("Please enter your bank name:")

        from_account = get_bank_account_number(from_bank.lower())

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
