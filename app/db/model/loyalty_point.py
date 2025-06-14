
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class LoyaltyPointTransaction(Base):
    __tablename__ = "loyalty_point_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    points = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)  # e.g., "booking", "admin_reward", "redeem"
    related_id = Column(Integer, nullable=True)  # optional: link to booking or reward
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="point_transactions")
