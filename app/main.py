from fastmcp import FastMCP
from app.logging_config import setup_logging
from app.tools import (
    account_tools,
    balance_tools,
    transaction_tools,
    bill_payment_tools,
    transfer_tools,
    client_agent_tool,
)


def create_app():
    setup_logging()

    mcp = FastMCP("BIA")

    account_tools.register(mcp)
    balance_tools.register(mcp)
    transaction_tools.register(mcp)
    bill_payment_tools.register(mcp)
    transfer_tools.register(mcp)
    transaction_tools.register(mcp)
    client_agent_tool.register(mcp)

    return mcp


def streamable_app():

    mcp = FastMCP("BIA")

    account_tools.register(mcp)
    balance_tools.register(mcp)
    transaction_tools.register(mcp)
    bill_payment_tools.register(mcp)
    transfer_tools.register(mcp)

    return mcp.http_app(transport="streamable-http")
