# BIA MCP

BIA MCP is a Python-based Model Context Protocol (MCP) server that exposes banking workflows through FastMCP tools.
It is designed for developer integration and local testing against bank mock services or real backend services.

## What This Project Provides

- Account context lookup for the currently logged-in user
- Balance retrieval per bank (`BPI`, `GCASH`)
- Transaction history retrieval per bank
- Bill payment against bank-supported billers
- Same-bank and interbank transfer flows
- Optional client-information AI agent (Azure OpenAI + Azure Cosmos DB)

## Architecture Overview

### Component Summary

- `run_sse.py`: starts FastMCP using SSE transport (`0.0.0.0:8000`), supports `-demo` mode
- `run_streamable_http`: starts FastMCP using streamable HTTP transport (`0.0.0.0:8000`)
- `run.py`: default local entrypoint (`app.run()`)
- `app/main.py`: MCP app factory and tool registration
- `app/tools/*`: MCP tool definitions exposed to clients
- `app/services/*`: business and integration logic (backend lookup, bank APIs, transfers, AI agent)
- `mock_backend.py`: local mock backend for user + bank account resolution

### Runtime Flow

```text
MCP Client (Claude Desktop / custom client)
        |
        v
FastMCP Server (BIA)
  - account tools
  - balance tools
  - transaction tools
  - bill payment tools
  - transfer tools
  - client information agent tool (optional)
        |
        +--> Backend Service (BIABACKENDURL)
        |      - resolve logged-in user
        |      - resolve bank account number
        |
        +--> Bank APIs (BANK1URL, BANK2URL)
        |      - balance
        |      - transactions
        |      - bill payment
        |      - same-bank transfer
        |
        +--> Clearing House (CLEARINGHOUSEURL)
        |      - interbank transfer
        |
        +--> Azure OpenAI + Cosmos DB (optional)
               - client_information_agent
```

## Prerequisites

- Python `3.11+` (recommended: `3.11.x` or `3.12.x`)
- `pip`
- Reachable dependent services:
  - bank APIs (`BANK1URL`, `BANK2URL`)
  - clearing house (`CLEARINGHOUSEURL`)
  - backend profile/account resolver (`BIABACKENDURL`)

Optional (only if using `client_information_agent`):

- Azure OpenAI deployment
- Azure Cosmos DB containers
- corresponding environment variables

## Environment Configuration

Create a `.env` file in the project root (same level as `README.md`):

```env
BANK1URL=http://localhost:8000
BANK2URL=http://localhost:8001
CLEARINGHOUSEURL=http://localhost:9000
BIABACKENDURL=http://127.0.0.1:9001

LOGGED_IN_USER=bia-8a62cd33-dae5-491a-8677-08d7843aadaa
USE_LOCAL_USER_FALLBACK=true

# Optional: bypass backend account lookup for demos
USE_DEMO_BANK_ACCOUNT_IDS=false
DEMO_GCASH_ACCOUNT_ID=GCASH001
DEMO_BPI_ACCOUNT_ID=BPI001

# Optional: client_information_agent
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT=
AZURE_OPENAI_API_VERSION=
COSMOS_ENDPOINT=
COSMOS_KEY=
```

## Setup and Run (OS-Specific)

| Step | macOS / Linux (bash/zsh) | Windows (PowerShell) | Windows (Command Prompt) |
| --- | --- | --- | --- |
| Go to project directory | `cd /path/to/BIA-MCP` | `cd C:\path\to\BIA-MCP` | `cd C:\path\to\BIA-MCP` |
| Create virtual environment | `python3.11 -m venv .venv` | `py -3.11 -m venv .venv` | `py -3.11 -m venv .venv` |
| Activate virtual environment | `source .venv/bin/activate` | `.\.venv\Scripts\Activate.ps1` | `.venv\Scripts\activate.bat` |
| Upgrade pip | `python -m pip install --upgrade pip` | `python -m pip install --upgrade pip` | `python -m pip install --upgrade pip` |
| Install dependencies | `pip install -r requirements.txt` | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| Run MCP server (SSE) | `python run_sse.py` | `python .\run_sse.py` | `python run_sse.py` |

## Feature-Based Usage Examples

These are MCP tool calls exposed by the server.

### 1. User and Account Context

```python
fetch_logged_in_user()
fetch_bank_account_number(bank="gcash")
```

Use this before account-dependent operations when validating environment wiring.

### 2. Balance Retrieval

```python
fetch_balance(bank="bpi")
```

Returns current balance for the logged-in user on the selected bank.

### 3. Transaction History

```python
fetch_transactions(bank="gcash")
```

Returns transactions list from the configured bank API.

### 4. Bill Payment

```python
get_billers_for_bank(bank="bpi")
pay_bill(
    bank="bpi",
    biller_code="MERALCO",
    reference_number="INV-10001",
    amount=1500,
)
```

### 5. Transfers

Same-bank transfer:

```python
transfer_funds(
    to_account_number="BPI002",
    to_bank="BPI",
    amount=500,
    from_bank="BPI",
)
```

Interbank transfer:

```python
transfer_funds(
    to_account_number="GCASH001",
    to_bank="GCASH",
    amount=800,
    from_bank="BPI",
)
```

### 6. Client Information Agent (Optional)

```python
client_information_agent(message="Update my mobile to 09171234567")
```

This tool requires Azure OpenAI and Cosmos DB configuration.

## Swagger-Style cURL Examples

The following samples use OpenAPI/Swagger-style `curl` formatting (`-X`, `accept`, `Content-Type`) for easier import/adaptation.

### Mock backend: health check

```bash
curl -X 'GET' \
  'http://127.0.0.1:9001/health' \
  -H 'accept: application/json'
```

### Mock backend: logged-in user profile

```bash
curl -X 'GET' \
  'http://127.0.0.1:9001/account/bia-8a62cd33-dae5-491a-8677-08d7843aadaa' \
  -H 'accept: application/json'
```

### Mock backend: bank account lookup

```bash
curl -X 'GET' \
  'http://127.0.0.1:9001/account/bank/bia-8a62cd33-dae5-491a-8677-08d7843aadaa/bpi' \
  -H 'accept: application/json'
```

## Command Walkthrough by OS

| Command Purpose | macOS / Linux (bash/zsh) | Windows (PowerShell) | Windows (Command Prompt) | Description |
| --- | --- | --- | --- | --- |
| Create venv | `python3.11 -m venv .venv` | `py -3.11 -m venv .venv` | `py -3.11 -m venv .venv` | Creates an isolated Python environment. |
| Activate venv | `source .venv/bin/activate` | `.\.venv\Scripts\Activate.ps1` | `.venv\Scripts\activate.bat` | Activates the project environment for the current shell. |
| Install dependencies | `pip install -r requirements.txt` | `pip install -r requirements.txt` | `pip install -r requirements.txt` | Installs FastMCP, HTTP tooling, and optional Azure/Cosmos packages. |
| Run SSE server | `python run_sse.py` | `python .\run_sse.py` | `python run_sse.py` | Runs MCP server on port `8000` with SSE transport. |
| Run SSE server in demo mode | `python run_sse.py -demo 001` | `python .\run_sse.py -demo 001` | `python run_sse.py -demo 001` | Starts demo account mode and in-process mock backend. |
| Run streamable HTTP mode | `python run_streamable_http` | `python .\run_streamable_http` | `python run_streamable_http` | Runs MCP server with streamable HTTP transport on port `8000`. |
| Run mock backend only | `python mock_backend.py` | `python .\mock_backend.py` | `python mock_backend.py` | Starts account/profile backend at `http://127.0.0.1:9001`. |

## Local Integration Example (Claude Desktop)

### Step-by-step setup (official MCP docs style)

This setup follows the official MCP user quickstart approach for Claude Desktop:
https://modelcontextprotocol.io/quickstart/user

1. Locate Claude Desktop config file:
   
   | OS | Config Path |
   | --- | --- |
   | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
   | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
2. Copy this repository sample as a starting point:
   - `demo/claude_desktop_config.json`
3. Update these fields for your machine:
   - `command`: absolute path to your local virtualenv Python executable
   - `args[0]`: absolute path to `/run.py` in this repository
   - `env`: your local `LOGGED_IN_USER`, backend URLs, and optional Azure/Cosmos settings
4. Save `claude_desktop_config.json`.
5. Restart Claude Desktop.
6. Verify the `BIA-MCP` server appears in Claude Desktop integrations/tools.

## Demo CSV to Unified Excel Workbook

The `demo` folder contains CSV inputs intended to be merged into a single workbook with two sheets:
- `bills-payment` from `demo/BIA-Excel-transfer.csv`
- `transactions` from `demo/BIA-Excel.csv`

| OS | Install Command | Convert Command |
| --- | --- | --- |
| macOS / Linux | `python -m pip install pandas openpyxl` | `python -c "import pandas as pd; w=pd.ExcelWriter('demo/BIA-Excel.xlsx', engine='openpyxl'); pd.read_csv('demo/BIA-Excel-transfer.csv').to_excel(w, sheet_name='bills-payment', index=False); pd.read_csv('demo/BIA-Excel.csv').to_excel(w, sheet_name='transactions', index=False); w.close(); print('Created demo/BIA-Excel.xlsx')"` |
| Windows (PowerShell / CMD) | `py -3.11 -m pip install pandas openpyxl` | `py -3.11 -c "import pandas as pd; w=pd.ExcelWriter('demo/BIA-Excel.xlsx', engine='openpyxl'); pd.read_csv('demo/BIA-Excel-transfer.csv').to_excel(w, sheet_name='bills-payment', index=False); pd.read_csv('demo/BIA-Excel.csv').to_excel(w, sheet_name='transactions', index=False); w.close(); print('Created demo/BIA-Excel.xlsx')"` |

## Notes for Developers

- Account-dependent tools call `BIABACKENDURL` to resolve the logged-in user's bank account ID.
- `USE_LOCAL_USER_FALLBACK=true` allows user profile fallback when backend user lookup fails.
- Transfer routing behavior:
  - `from_bank == to_bank`: calls bank `/transfer`
  - `from_bank != to_bank`: calls clearing house `/interbank-transfer`
- Supported banks in this codebase are currently `BPI` and `GCASH`.

## License

Provided as-is for educational and hackathon purposes.
