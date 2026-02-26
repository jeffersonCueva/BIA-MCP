#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


HOST = os.getenv("MOCK_BACKEND_HOST", "127.0.0.1")
PORT = int(os.getenv("MOCK_BACKEND_PORT", "9001"))


HARDCODED_USER_ID = "bia-8a62cd33-dae5-491a-8677-08d7843aadaa"


def build_users(
    user_id: str = HARDCODED_USER_ID,
    gcash_account: str = "1000000001",
    bpi_account: str = "2000000001",
):
    return {
        user_id: {
            "userId": user_id,
            "fullName": "Christian Lazatin",
            "email": "christian@example.com",
            "mobile": "09171234567",
            "accounts": {
                "gcash": gcash_account,
                "bpi": bpi_account,
            },
        },
    }


# Minimal in-memory dataset for local MCP testing.
USERS = build_users()


def create_handler(users):
    class MockBackendHandler(BaseHTTPRequestHandler):
        def _send_json(self, status_code: int, payload: dict):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            return

        def do_GET(self):
            path = urlparse(self.path).path
            parts = [p for p in path.split("/") if p]

            # GET /health
            if parts == ["health"]:
                return self._send_json(200, {"status": "ok"})

            # GET /account/{user_id}
            if len(parts) == 2 and parts[0] == "account":
                user_id = parts[1]
                user = users.get(user_id)
                if not user:
                    return self._send_json(404, {"detail": "User not found"})
                return self._send_json(
                    200,
                    {
                        "userId": user["userId"],
                        "fullName": user["fullName"],
                        "email": user["email"],
                        "mobile": user["mobile"],
                    },
                )

            # GET /account/bank/{user_id}/{bank}
            if len(parts) == 4 and parts[0] == "account" and parts[1] == "bank":
                user_id = parts[2]
                bank = parts[3].lower()
                user = users.get(user_id)
                if not user:
                    return self._send_json(404, {"detail": "User not found"})
                account_number = user["accounts"].get(bank)
                if not account_number:
                    return self._send_json(404, {"detail": f"Bank account not found: {bank}"})
                return self._send_json(
                    200,
                    {
                        "userId": user_id,
                        "bank": bank,
                        "accountNumber": account_number,
                    },
                )

            return self._send_json(404, {"detail": "Not found"})

    return MockBackendHandler


def create_server(host: str = HOST, port: int = PORT, users=None):
    if users is None:
        users = USERS
    return HTTPServer((host, port), create_handler(users))


def main():
    server = create_server(HOST, PORT, USERS)
    print(f"Mock backend running at http://{HOST}:{PORT}")
    print("Endpoints:")
    print("  GET /health")
    print("  GET /account/{user_id}")
    print("  GET /account/bank/{user_id}/{bank}")
    server.serve_forever()


if __name__ == "__main__":
    main()
