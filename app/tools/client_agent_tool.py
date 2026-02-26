from fastmcp import FastMCP
from app.services.client_information_agent import ClientInformationAgent


def register(mcp: FastMCP):
    agent = ClientInformationAgent()

    @mcp.tool()
    async def client_information_agent(message: str) -> dict:
        return await agent.handle_message(message)

