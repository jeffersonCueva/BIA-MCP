from fastmcp import FastMCP
import logging
import httpx

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("BIA")

# -----------------------------
# Bank registry
# -----------------------------
BANK_APIS = {
    "gcash": "http://localhost:8002",
    "bpi": "http://localhost:8003",
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
# Bill Payment helpers
# -----------------------------
def _fetch_billers_for_bank(bank: str) -> dict:
    bank = bank.strip()
    logging.info(f"Fetching billers for bank: {bank}")
    api = BANK_APIS.get(bank.lower())
    if not api:
        return {}

    try:
        resp = httpx.get(f"{api}/supported-billers", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, dict):
            billers = data
        elif isinstance(data, list):
            if data and isinstance(data[0], dict):
                billers = {item.get("code", "").upper(): item.get("name", "") for item in data}
            else:
                billers = {str(item).upper(): str(item) for item in data}
        else:
            billers = {}
        return {k.strip().upper(): v for k, v in billers.items() if k}
    except httpx.HTTPError as e:
        logging.error(f"Error fetching billers from {bank}: {e}")
        return {}


@mcp.tool()
def get_billers_for_bank(bank: str) -> dict:
    return _fetch_billers_for_bank(bank)

@mcp.tool()
def pay_bill(
    user: str,
    bank: str,
    biller_code: str,
    reference_number: str,
    amount: int,
) -> str:
    bank = bank.strip()
    biller_code = biller_code.strip().upper()
    logging.info(
        f"Bill payment request: {user}@{bank} paying {amount} "
        f"to biller {biller_code} (ref: {reference_number})"
    )

    api = BANK_APIS.get(bank.lower())
    if not api:
        logging.error(f"Unknown bank: {bank}")
        return f"Unknown bank: {bank}"

    try:
        bank_billers = _fetch_billers_for_bank(bank)
    except Exception as e:
        logging.error(f"Failed to fetch billers for {bank}: {e}")
        bank_billers = {}

    if biller_code not in bank_billers:
        logging.error(f"Unsupported biller code: {biller_code} for bank {bank}")
        return f"Unsupported biller code: {biller_code} for bank {bank}. Supported: {list(bank_billers.keys())}"

    if amount <= 0:
        logging.error(f"Invalid bill payment amount: {amount}")
        return "Amount must be greater than 0."

    payload = {
        "account_holder": user,
        "biller_code": biller_code,
        "reference_number": reference_number,
        "amount": amount,
    }

    try:
        response = httpx.post(f"{api}/bill-payment", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        logging.info(f"Bill payment successful: {result}")
        return result.get("message", "Bill payment completed successfully.")
    except httpx.HTTPError as e:
        logging.error(f"Bill payment failed: {e}")
        return "Bill payment failed. Please try again later."

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
