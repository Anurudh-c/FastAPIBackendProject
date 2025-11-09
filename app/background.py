import time
from app.crud import mark_transaction_processed, get_transaction
from app.database import SessionLocal

def process_transaction_worker(transaction_id: str, delay_seconds: int = 30):
   
    time.sleep(delay_seconds)

    db = SessionLocal()
    try:
        tx = get_transaction(db, transaction_id)
        if not tx:
            return
        if tx.status == tx.status.__class__.PROCESSED:
            return
        mark_transaction_processed(db, transaction_id)
    finally:
        db.close()
