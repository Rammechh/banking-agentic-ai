import asyncio
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"

SERVER_PATHS = {
    "accounts": "mcp_servers/accounts_server.py",
    "transactions": "mcp_servers/transactions_server.py",
    "service": "mcp_servers/service_server.py",
}


def classify_intent(user_query: str) -> str:
    prompt = f"""You are a routing classifier for a bank's customer service system.
Classify the user's query into EXACTLY ONE of these categories:
- accounts (balance enquiries)
- transactions (transaction history, statements)
- service (cheque book requests, address changes, KYC updates)

Respond with ONLY the category word, nothing else.

User query: "{user_query}"
Category:"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME, "prompt": prompt, "stream": False
    })
    result = response.json()["response"].strip().lower()

    for category in ["accounts", "transactions", "service"]:
        if category in result:
            return category
    return "service"


async def call_mcp_tool(server_path: str, tool_name: str, arguments: dict) -> dict:
    """Launch an MCP server as a subprocess, call one tool on it, then shut it down."""
    server_params = StdioServerParameters(command="python3", args=[server_path])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text if result.content else {}


async def coordinator(user_query: str, account_id: str) -> dict:
    intent = classify_intent(user_query)
    print(f"[Coordinator] Classified intent: {intent}")

    if intent == "accounts":
        return await call_mcp_tool(SERVER_PATHS["accounts"], "get_balance", {"account_id": account_id})
    elif intent == "transactions":
        return await call_mcp_tool(SERVER_PATHS["transactions"], "get_transactions", {"account_id": account_id})
    elif intent == "service":
        return await call_mcp_tool(SERVER_PATHS["service"], "request_chequebook", {"account_id": account_id})
    else:
        return {"error": "Could not classify request"}


if __name__ == "__main__":
    test_query = input("Ask your banking question: ")
    result = asyncio.run(coordinator(test_query, account_id="AC001"))
    print(result)