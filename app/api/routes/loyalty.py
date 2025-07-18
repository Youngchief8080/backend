from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.model.loyalty_point import LoyaltyPointTransaction
from app.schemas.loyalty_point import LoyaltyPointTransactionCreate, LoyaltyPointTransactionOut , LoyaltyAdjustmentRequest
from typing import List
from app.db.model.user import User

router = APIRouter()

@router.post("/loyalty-points/", response_model=LoyaltyPointTransactionOut)
def create_loyalty_transaction(data: LoyaltyPointTransactionCreate, db: Session = Depends(get_db)):
    txn = LoyaltyPointTransaction(**data.dict())
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn

@router.get("/loyalty-points/user/{user_id}", response_model=List[LoyaltyPointTransactionOut])
def get_user_loyalty_history(user_id: int, db: Session = Depends(get_db)):
    return db.query(LoyaltyPointTransaction)\
        .filter(LoyaltyPointTransaction.user_id == user_id)\
        .order_by(LoyaltyPointTransaction.created_at.desc())\
        .all()


@router.get("/loyalty/user/{user_id}/booking/{booking_id}")
def get_loyalty_points_for_booking(user_id: int, booking_id: int, reason: str = "booking", db: Session = Depends(get_db)):
    txn = db.query(LoyaltyPointTransaction)\
        .filter_by(user_id=user_id, related_id=booking_id, reason=reason)\
        .first()

    if not txn:
        raise HTTPException(status_code=404, detail="Loyalty transaction not found")
    
    return {"points": txn.points}


@router.post("/loyalty-points/adjust/")
def adjust_user_loyalty_points(payload: LoyaltyAdjustmentRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_balance = (user.loyalty_points or 0) + payload.points
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Cannot reduce points below 0")
    user.loyalty_points = new_balance
    txn = LoyaltyPointTransaction(
        user_id=user.id,
        points=payload.points,
        reason=payload.reason,
        related_id=None  # since this is manual
    )
    db.add(txn)
    db.commit()
    db.refresh(user)
    return {
        "message": "Points adjusted successfully",
        "user_id": user.id,
        "new_balance": user.loyalty_points
    }


