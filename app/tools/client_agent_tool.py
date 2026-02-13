from fastmcp.server import FastMCP
from app.agents.client_information_agent import ClientInformationAgent

mcp = FastMCP("ClientInformationAgentServer")
agent = ClientInformationAgent()

@mcp.tool()
def client_information_agent(message: str) -> dict:
    return agent.handle_message(message)


