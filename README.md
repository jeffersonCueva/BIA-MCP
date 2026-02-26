# BIA MCP

This project provides a Python-based banking toolset built using **FastMCP**. It allows you to:

* Retrieve user balances from different banks.
* Fetch transaction histories.
* Transfer funds between users within the same bank and across banks via a clearing house.

---

## Prerequisites

Make sure you have the following installed:

* **Python 3.11+** (3.13 recommended on macOS)

Create and activate a Python 3.11 virtual environment, then install dependencies:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python --version  # should print 3.11.x or newer
pip install -r requirements.txt
```

---

## Configuration

1. **Bank APIs:**
   Update the `BANK_APIS` dictionary with the URLs of the banks you want to connect.

```python
BANK_APIS = {
    "gcash": "http://localhost:8002",
    "bpi": "http://localhost:8003",
}
```

2. **Clearing House:**
   Set the clearing house API endpoint for interbank transfers.

```python
CLEARING_HOUSE_API = "http://localhost:9000"
```

3. **Demo account ID mode (optional):**
   If your backend returns user IDs (for example `bia-...`) and you need bank-formatted IDs for demo calls, you can enable:

```bash
USE_DEMO_BANK_ACCOUNT_IDS=true
DEMO_GCASH_ACCOUNT_ID=GCASH001
DEMO_BPI_ACCOUNT_ID=BPI001
```

Or pass it at runtime for SSE:

```bash
python run_sse.py -demo 001
```

This starts an in-process mock backend (same behavior as `mock_backend.py`) and serves demo
account IDs `GCASH001` and `BPI001` for that run only.

Without `-demo`, `run_sse.py` keeps the normal flow and resolves account IDs using
`LOGGED_IN_USER` via `BIABACKENDURL`.

---

## Tools Provided

### 1. Get Balance

```python
get_balance(user: str, bank: str) -> int
```

* Fetches the balance for a user in a specific bank.

### 2. Get Transactions

```python
get_transactions(user: str, bank: str) -> list
```

* Retrieves the transaction history for a user.

### 3. Pay Bill

```python
pay_bill(user: str, bank: str, biller_code: str, reference_number: str, amount: int) -> str
```

* Pay bills through any registered bank.
* Supports multiple billers with different biller codes.
* Requires account holder name, bank, biller details, and payment amount.

### 4. Transfer Funds

```python
transfer_funds(from_user: str, from_bank: str, to_user: str, to_bank: str, amount: int) -> str
```

* Supports same-bank and interbank transfers.
* Uses the clearing house for interbank transactions.

---

## Running the MCP Server

Run the MCP instance using one of the provided entrypoints:

```bash
python run_sse.py
```

Alternative transport:

```bash
python run_streamable_http
```

Once running, the MCP instance `BIA` will expose the tools for use in other applications or automation workflows.

### Local Mock Backend (for account lookup testing)

This repo includes a lightweight mock backend that serves:

* `GET /account/{user_id}`
* `GET /account/bank/{user_id}/{bank}`

Run it in a separate terminal:

```bash
python mock_backend.py
```

It listens on `http://127.0.0.1:9001` by default, matching `BIABACKENDURL`.

---

## Logging

* Logging is enabled at the **INFO** level.
* Errors in HTTP requests are logged with details for debugging purposes.

---

## Notes

* Ensure all backend bank APIs and the clearing house are running before making requests.
* Timeout settings are configured for each API call (5–10 seconds depending on operation).
* Intended for development/demo purposes.

---

## License

Provided as-is for educational and hackathon purposes.
