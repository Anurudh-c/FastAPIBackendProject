from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app import models

def create_transaction_if_not_exists(db: Session, tx_data: dict):
    existing = db.query(models.Transaction).filter(models.Transaction.transaction_id == tx_data["transaction_id"]).first()
    if existing:
        return existing, False

    tx = models.Transaction(
        transaction_id=tx_data["transaction_id"],
        source_account=tx_data["source_account"],
        destination_account=tx_data["destination_account"],
        amount=tx_data["amount"],
        currency=tx_data["currency"],
        status=models.TransactionStatus.PROCESSING
    )
    db.add(tx)
    try:
        db.commit()
        db.refresh(tx)
        return tx, True
    except IntegrityError:
        db.rollback()
        existing = db.query(models.Transaction).filter(models.Transaction.transaction_id == tx_data["transaction_id"]).first()
        return existing, False

def mark_transaction_processed(db: Session, transaction_id: str):
    tx = db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
    if not tx:
        return None
    if tx.status == models.TransactionStatus.PROCESSED:
        return tx
    tx.status = models.TransactionStatus.PROCESSED
    tx.processed_at = datetime.utcnow()
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def get_transaction(db: Session, transaction_id: str):
    return db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()
