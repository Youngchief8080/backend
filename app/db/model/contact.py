from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.base import Base
from app.db.model.user import User

class ContactStatus(str, Enum):
    PENDING = 'pending'
    PROCESSED = 'processed'
    REJECTED = 'rejected'

class ContactModel(Base):
    """Represents contact form submissions from users."""
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), index=True)
    message = Column(String(2000), index=True)  
    status = Column(String(50), index=True, default=ContactStatus.PENDING)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    user_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # user = relationship("User", back_populates="contacts")