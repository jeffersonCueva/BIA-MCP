import os

BANK_APIS = {
    "gcash": "http://localhost:8000",
    "bpi": "http://localhost:8001",
}

CLEARING_HOUSE_API = "http://localhost:9000"
BIA_BACKEND = "http://localhost:9001"

LOGGED_IN_USER = os.getenv("LOGGED_IN_USER", "None")
