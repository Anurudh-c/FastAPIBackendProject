# app/main.py
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app import schemas, crud
from app.database import engine, Base, get_db
from app.background import process_transaction_worker

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Transactions Webhook Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    now = datetime.now(timezone.utc).isoformat()
    return {"status": "HEALTHY", "current_time": now}

@app.post("/v1/webhooks/transactions", status_code=202)
def receive_webhook(payload: schemas.TransactionIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    data = payload.dict()

    tx, created = crud.create_transaction_if_not_exists(db, data)

    if not created:
        return JSONResponse(status_code=202, content={"detail": "Already received"})

    background_tasks.add_task(process_transaction_worker, tx.transaction_id, 30)

    return JSONResponse(status_code=202, content={"detail": "Accepted"})

@app.get("/v1/transactions/{transaction_id}", response_model=schemas.TransactionOut)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    tx = crud.get_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx
