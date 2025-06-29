
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class GetintouchModel(Base):
    """Represents contact form submissions from users."""
    __tablename__ = "getintouchs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    message = Column(String(2000), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

