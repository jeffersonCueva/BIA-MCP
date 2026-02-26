from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from project root regardless of current working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BANK1 = os.getenv("BANK1URL", "http://localhost:8000")
BANK2 = os.getenv("BANK2URL", "http://localhost:8001")
CLEARING_HOUSE_API = os.getenv("CLEARINGHOUSEURL", "http://localhost:9000")
BIA_BACKEND = os.getenv("BIABACKENDURL", "http://localhost:9001")

BANK_APIS = {
    "gcash": BANK1,
    "bpi": BANK2,
}

# Temporary hardcoded fallback for local/Claude Desktop runs.
HARDCODED_LOGGED_IN_USER = "bia-8a62cd33-dae5-491a-8677-08d7843aadaa"
LOGGED_IN_USER = os.getenv("LOGGED_IN_USER", HARDCODED_LOGGED_IN_USER).strip()

# Local fallback mode when BIABACKENDURL is unavailable.
USE_LOCAL_USER_FALLBACK = os.getenv("USE_LOCAL_USER_FALLBACK", "true").lower() == "true"
LOCAL_USER_PROFILE = {
    "userId": LOGGED_IN_USER,
    "fullName": os.getenv("LOCAL_USER_FULLNAME", "Local Test User"),
    "email": os.getenv("LOCAL_USER_EMAIL", "local.user@example.com"),
    "mobile": os.getenv("LOCAL_USER_MOBILE", "09171234567"),
}

# Demo fallback for bank account IDs used by bank endpoints.
# When enabled, backend account lookup is skipped and these values are returned.
USE_DEMO_BANK_ACCOUNT_IDS = os.getenv("USE_DEMO_BANK_ACCOUNT_IDS", "false").lower() == "true"
DEMO_BANK_ACCOUNT_IDS = {
    "gcash": os.getenv("DEMO_GCASH_ACCOUNT_ID", "GCASH001"),
    "bpi": os.getenv("DEMO_BPI_ACCOUNT_ID", "BPI001"),
}
