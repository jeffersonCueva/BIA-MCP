import argparse
import os
import threading
from urllib.parse import urlparse


def _build_demo_account_id(prefix: str, demo_suffix: str) -> str:
    value = (demo_suffix or "").strip()
    if value.isdigit():
        value = value.zfill(3)
    return f"{prefix}{value}"


def _parse_backend_host_port(backend_url: str):
    parsed = urlparse(backend_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    return host, port


def _start_demo_backend(demo_suffix: str):
    from mock_backend import HARDCODED_USER_ID, build_users, create_server

    backend_url = os.getenv("BIABACKENDURL", "http://127.0.0.1:9001")
    host, port = _parse_backend_host_port(backend_url)
    user_id = os.getenv("LOGGED_IN_USER", HARDCODED_USER_ID).strip() or HARDCODED_USER_ID

    users = build_users(
        user_id=user_id,
        gcash_account=_build_demo_account_id("GCASH", demo_suffix),
        bpi_account=_build_demo_account_id("BPI", demo_suffix),
    )

    try:
        server = create_server(host, port, users)
    except OSError as exc:
        print(f"[demo] Could not start mock backend at {backend_url}: {exc}")
        print("[demo] Continuing startup; existing backend (if any) will be used.")
        return

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"[demo] Mock backend running at {backend_url} for user {user_id}")


def main():
    parser = argparse.ArgumentParser(description="Run BIA MCP server (SSE transport)")
    parser.add_argument(
        "-demo",
        "--demo",
        dest="demo_suffix",
        metavar="SUFFIX",
        help="Enable demo mode and use account IDs GCASH<suffix> / BPI<suffix> (e.g. 001)",
    )
    args = parser.parse_args()

    if args.demo_suffix:
        # Demo mode should mimic running mock_backend.py while keeping normal tool flow.
        os.environ["USE_DEMO_BANK_ACCOUNT_IDS"] = "false"
        os.environ["DEMO_GCASH_ACCOUNT_ID"] = _build_demo_account_id("GCASH", args.demo_suffix)
        os.environ["DEMO_BPI_ACCOUNT_ID"] = _build_demo_account_id("BPI", args.demo_suffix)
        _start_demo_backend(args.demo_suffix)

    from app.main import create_app

    app = create_app()
    app.run(transport="sse", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
