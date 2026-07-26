import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
BANK_API_URL = "http://localhost:8000"
MODEL_NAME = "llama3.1:8b"  # match whatever you pulled


def classify_intent(user_query: str) -> str:
    """Ask Ollama to classify the user's query into one of three categories."""
    prompt = f"""You are a routing classifier for a bank's customer service system.
Classify the user's query into EXACTLY ONE of these categories:
- accounts (balance enquiries)
- transactions (transaction history, statements)
- service (cheque book requests, address changes, KYC updates)

Respond with ONLY the category word, nothing else.

User query: "{user_query}"
Category:"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    result = response.json()["response"].strip().lower()

    # Keep only known categories, default to "service" if the model says something odd
    for category in ["accounts", "transactions", "service"]:
        if category in result:
            return category
    return "service"


def accounts_agent(account_id: str) -> dict:
    resp = requests.get(f"{BANK_API_URL}/accounts/{account_id}/balance")
    return resp.json()


def transactions_agent(account_id: str) -> dict:
    resp = requests.get(f"{BANK_API_URL}/accounts/{account_id}/transactions")
    return resp.json()


def service_agent(account_id: str, request_type: str) -> dict:
    if request_type == "chequebook":
        resp = requests.post(f"{BANK_API_URL}/accounts/{account_id}/chequebook-request")
        return resp.json()
    return {"message": "Service type not yet handled"}


def coordinator(user_query: str, account_id: str) -> dict:
    """Main entry point: classify, then route to the right agent."""
    intent = classify_intent(user_query)
    print(f"[Coordinator] Classified intent: {intent}")

    if intent == "accounts":
        return accounts_agent(account_id)
    elif intent == "transactions":
        return transactions_agent(account_id)
    elif intent == "service":
        return service_agent(account_id, "chequebook")  # simplified for now
    else:
        return {"error": "Could not classify request"}


if __name__ == "__main__":
    test_query = input("Ask your banking question: ")
    result = coordinator(test_query, account_id="AC001")
    print(json.dumps(result, indent=2))