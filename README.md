# BIA MCP

This project provides a Python-based banking toolset built using **FastMCP**. It allows you to:

* Retrieve user balances from different banks.
* Fetch transaction histories.
* Transfer funds between users within the same bank and across banks via a clearing house.

---

## Prerequisites

Make sure you have the following installed:

* **Python 3.13**

Install dependencies using:

```bash
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

Run the FastMCP development server to start the MCP instance and register all tools:

```bash
fastmcp dev server.py
```

* Replace `server.py` with the filename of your script if different.
* Once running, the MCP instance `BIA` will expose the tools for use in other applications or automation workflows.

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
