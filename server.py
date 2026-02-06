from fastmcp import FastMCP
import logging
import httpx

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("BIA")

# -----------------------------
# Bank registry
# -----------------------------
BANK_APIS = {
    "gcash": "http://localhost:8000",
    "bpi": "http://localhost:8001",
}

CLEARING_HOUSE_API = "http://localhost:9000"


# -----------------------------
# Balance
# -----------------------------
@mcp.tool()
def get_balance(user: str, bank: str) -> int:
    """
    Get the balance of a user from a specific bank.
    """
    logging.info(f"Balance inquiry for {user} @ {bank}")

    api = BANK_APIS.get(bank.lower())
    if not api:
        return 0

    try:
        response = httpx.get(f"{api}/balance/{user}", timeout=5)
        response.raise_for_status()
        return response.json().get("balance", 0)

    except httpx.HTTPError as e:
        logging.error(e)
        return 0


# -----------------------------
# Transactions
# -----------------------------
@mcp.tool()
def get_transactions(user: str, bank: str) -> list:
    """
    Get transaction history for a user from a specific bank.
    """
    logging.info(f"Transaction history request for {user} @ {bank}")

    api = BANK_APIS.get(bank.lower())
    if not api:
        return []

    try:
        response = httpx.get(f"{api}/transactions/{user}", timeout=5)
        response.raise_for_status()
        data = response.json()

        return data.get("transactions", data)

    except httpx.HTTPError as e:
        logging.error(e)
        return []


# -----------------------------
# Transfers (same-bank + interbank)
# -----------------------------
@mcp.tool()
def transfer_funds(
    from_user: str,
    from_bank: str,
    to_user: str,
    to_bank: str,
    amount: int,
) -> str:
    """
    Transfer funds between users.
    Supports same-bank and interbank transfers.
    """

    logging.info(
        f"Transfer {amount} from {from_user}@{from_bank} " f"to {to_user}@{to_bank}"
    )

    # -----------------------------
    # Same-bank transfer
    # -----------------------------
    if from_bank.lower() == to_bank.lower():
        api = BANK_APIS.get(from_bank.lower())
        if not api:
            return "Unknown bank."

        payload = {
            "from_account": from_user,
            "to_account": to_user,
            "from_bank": from_bank,
            "to_bank": to_bank,
            "amount": amount,
        }

        try:
            response = httpx.post(
                f"{api}/transfer",
                json=payload,
                timeout=5,
            )
            response.raise_for_status()
            return response.json().get("message", "Transfer successful.")

        except httpx.HTTPError as e:
            logging.error(e)
            return "Transfer failed."

    # -----------------------------
    # Interbank transfer
    # -----------------------------
    payload = {
        "from_bank": from_bank,
        "from_account": from_user,
        "to_bank": to_bank,
        "to_account": to_user,
        "amount": amount,
    }

    try:
        response = httpx.post(
            f"{CLEARING_HOUSE_API}/interbank-transfer",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()

        return response.json().get(
            "message", "Interbank transfer completed successfully."
        )

    except httpx.HTTPError as e:
        logging.error(e)
        return "Interbank transfer failed."


if __name__ == "__main__":
    mcp.run()
