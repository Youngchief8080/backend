from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# For creating a new transaction
class LoyaltyPointTransactionCreate(BaseModel):
    user_id: int
    points: int
    reason: str
    related_id: Optional[int] = None

    class Config:
        orm_mode = True

# For returning a transaction (e.g., in history)
class LoyaltyPointTransactionOut(BaseModel):
    id: int
    reason: str
    points: int
    created_at: datetime

    class Config:
        orm_mode = True

# For admin adjustment endpoint
class LoyaltyAdjustmentRequest(BaseModel):
    user_id: int
    points: int  # can be positive or negative
    reason: str = "Pointed Add"

    class Config:
        orm_mode = True
