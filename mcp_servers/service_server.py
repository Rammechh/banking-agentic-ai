from mcp.server.fastmcp import FastMCP
import requests

BANK_API_URL = "http://localhost:8000"

mcp = FastMCP("Service MCP Server")


@mcp.tool()
def request_chequebook(account_id: str) -> dict:
    """Submit a request for a new cheque book to be delivered to the account holder."""
    resp = requests.post(f"{BANK_API_URL}/accounts/{account_id}/chequebook-request")
    if resp.status_code != 200:
        return {"error": f"Account {account_id} not found"}
    return resp.json()


@mcp.tool()
def update_address(account_id: str, new_address: str) -> dict:
    """Update the registered address for a bank account."""
    resp = requests.post(
        f"{BANK_API_URL}/accounts/{account_id}/update-address",
        json={"new_address": new_address}
    )
    if resp.status_code != 200:
        return {"error": f"Account {account_id} not found"}
    return resp.json()


@mcp.tool()
def update_kyc(account_id: str, document_type: str, document_number: str) -> dict:
    """Submit updated KYC documents for verification on a bank account."""
    resp = requests.post(
        f"{BANK_API_URL}/accounts/{account_id}/kyc-update",
        json={"document_type": document_type, "document_number": document_number}
    )
    if resp.status_code != 200:
        return {"error": f"Account {account_id} not found"}
    return resp.json()


if __name__ == "__main__":
    mcp.run()