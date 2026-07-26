from mcp.server.fastmcp import FastMCP
import requests

BANK_API_URL = "http://localhost:8000"

mcp = FastMCP("Transactions MCP Server")


@mcp.tool()
def get_transactions(account_id: str, limit: int = 10) -> dict:
    """Get recent transaction history for a bank account."""
    resp = requests.get(f"{BANK_API_URL}/accounts/{account_id}/transactions", params={"limit": limit})
    if resp.status_code != 200:
        return {"error": f"Account {account_id} not found"}
    return resp.json()


@mcp.tool()
def get_statement(account_id: str, days: int = 30) -> dict:
    """Get an account statement for a given number of past days."""
    resp = requests.get(f"{BANK_API_URL}/accounts/{account_id}/statement", params={"days": days})
    if resp.status_code != 200:
        return {"error": f"Account {account_id} not found"}
    return resp.json()


if __name__ == "__main__":
    mcp.run()