from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base import Base
import uuid

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    sender = Column(String, nullable=False)
    sender_id = Column(String, nullable=True)  # Temporary
    recipient = Column(String, nullable=True)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)
    reply_to = Column(String, ForeignKey('chat_messages.id'), nullable=True)
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, sender='{self.sender}', recipient='{self.recipient}', timestamp={self.timestamp})>"