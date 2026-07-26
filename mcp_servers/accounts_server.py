from mcp.server.fastmcp import FastMCP
import requests

BANK_API_URL = "http://localhost:8000"

mcp = FastMCP("Accounts MCP Server")


@mcp.tool()
def get_balance(account_id: str) -> dict:
    """Get the current balance for a bank account. Returns balance and currency."""
    resp = requests.get(f"{BANK_API_URL}/accounts/{account_id}/balance")
    if resp.status_code != 200:
        return {"error": f"Account {account_id} not found"}
    return resp.json()


if __name__ == "__main__":
    mcp.run()