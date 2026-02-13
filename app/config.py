from dotenv import load_dotenv
import os

load_dotenv()

BANK1 = os.getenv("BANK1URL", "http://localhost:8000")
BANK2 = os.getenv("BANK2URL", "http://localhost:8001")
CLEARING_HOUSE_API = os.getenv("CLEARINGHOUSEURL", "http://localhost:9000")
BIA_BACKEND = os.getenv("BIABACKENDURL", "http://localhost:9001")

BANK_APIS = {
    "gcash": BANK1,
    "bpi": BANK2,
}

LOGGED_IN_USER = os.getenv("LOGGED_IN_USER", "None")
