# Transactions Webhook Service

## Setup (local)
1. Create virtualenv:
   python -m venv .venv
   source .venv/bin/activate

2. Install:
   pip install -r requirements.txt

3. Run:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Default DB: SQLite file `transactions.db` created in project root.

## API

Health:
GET  / 
Response: {"status":"HEALTHY","current_time":"...Z"}

Webhook:
POST /v1/webhooks/transactions
Body:
{
  "transaction_id":"txn_abc123def456",
  "source_account":"acc_user_789",
  "destination_account":"acc_merchant_456",
  "amount":1500,
  "currency":"INR"
}
Response: 202 Accepted (fast)

Query:
GET /v1/transactions/{transaction_id}
Response: transaction details.

## Tests (curl)

1) Send webhook:
curl -X POST "http://127.0.0.1:8000/v1/webhooks/transactions" \
 -H "Content-Type: application/json" \
 -d '{"transaction_id":"txn_1","source_account":"acc_user_1","destination_account":"acc_2","amount":100,"currency":"INR"}' -i

You get 202.

2) Check immediately:
curl "http://127.0.0.1:8000/v1/transactions/txn_1"
status will be PROCESSING.

3) Wait ~30s then check:
status will be PROCESSED and processed_at set.

4) Send same webhook again:
You will get 202 but no duplicate processing.

## Notes
- This uses FastAPI BackgroundTasks. For production scale, use Celery/RQ with Redis. 
- For production DB use PostgreSQL set via DATABASE_URL env var.
