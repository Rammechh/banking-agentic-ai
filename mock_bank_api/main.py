from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

app = FastAPI(title="Mock Bank API")

# ---------- Fake seeded data ----------
accounts_db = {
    "AC001": {"customer_name": "Ramkumar", "balance": 45230.50, "currency": "INR",
               "address": "12 MG Road, Chennai", "kyc_status": "verified"},
    "AC002": {"customer_name": "Priya", "balance": 128900.00, "currency": "INR",
               "address": "45 Anna Nagar, Chennai", "kyc_status": "pending"},
}

transactions_db = {
    "AC001": [
        {"txn_id": "T1001", "date": "2026-07-20", "description": "UPI - Swiggy", "amount": -450.00},
        {"txn_id": "T1002", "date": "2026-07-18", "description": "Salary Credit", "amount": 55000.00},
        {"txn_id": "T1003", "date": "2026-07-15", "description": "ATM Withdrawal", "amount": -2000.00},
    ],
    "AC002": [
        {"txn_id": "T2001", "date": "2026-07-22", "description": "Electricity Bill", "amount": -1800.00},
    ],
}

service_requests_db = []  # holds cheque book / address / KYC requests as they come in


# ---------- Request body models ----------
class AddressUpdateRequest(BaseModel):
    new_address: str

class KYCUpdateRequest(BaseModel):
    document_type: str
    document_number: str


# ---------- Root ----------
@app.get("/")
def root():
    return {"message": "Mock Bank API is running"}


# ---------- Accounts Agent endpoints ----------
@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: str):
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account_id, "balance": account["balance"], "currency": account["currency"]}


# ---------- Transactions Agent endpoints ----------
@app.get("/accounts/{account_id}/transactions")
def get_transactions(account_id: str, limit: int = 10):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    txns = transactions_db.get(account_id, [])
    return {"account_id": account_id, "transactions": txns[:limit]}


@app.get("/accounts/{account_id}/statement")
def get_statement(account_id: str, days: int = 30):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    cutoff = datetime.now() - timedelta(days=days)
    txns = transactions_db.get(account_id, [])
    filtered = [t for t in txns if datetime.strptime(t["date"], "%Y-%m-%d") >= cutoff]
    return {"account_id": account_id, "period_days": days, "transactions": filtered}


# ---------- Service Agent endpoints ----------
@app.post("/accounts/{account_id}/chequebook-request")
def request_chequebook(account_id: str):
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    request_id = str(uuid.uuid4())[:8]
    service_requests_db.append({
        "request_id": request_id, "account_id": account_id,
        "type": "chequebook", "status": "submitted"
    })
    return {"request_id": request_id, "status": "submitted", "message": "Cheque book will be delivered in 5-7 business days"}


@app.post("/accounts/{account_id}/update-address")
def update_address(account_id: str, body: AddressUpdateRequest):
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account["address"] = body.new_address
    request_id = str(uuid.uuid4())[:8]
    service_requests_db.append({
        "request_id": request_id, "account_id": account_id,
        "type": "address_update", "status": "completed"
    })
    return {"request_id": request_id, "status": "completed", "new_address": account["address"]}


@app.post("/accounts/{account_id}/kyc-update")
def update_kyc(account_id: str, body: KYCUpdateRequest):
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account["kyc_status"] = "under_review"
    request_id = str(uuid.uuid4())[:8]
    service_requests_db.append({
        "request_id": request_id, "account_id": account_id,
        "type": "kyc_update", "status": "under_review",
        "document_type": body.document_type
    })
    return {"request_id": request_id, "status": "under_review", "message": "KYC documents received, verification in progress"}