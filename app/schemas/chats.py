from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    id: str
    sender: str
    sender_id: str
    content: str
    timestamp: datetime
    is_admin: bool = False
    recipient: Optional[str] = None
    reply_to: Optional[str] = None

    class Config:
        orm_mode = True

class WebSocketMessage(BaseModel):
    type: str  # 'message', 'notification', 'error', etc.
    id: str
    content: str
    sender: Optional[str] = None
    senderId: Optional[str] = None
    recipient: Optional[str] = None
    timestamp: Optional[datetime] = None
    is_own: Optional[bool] = None
    reply_to: Optional[str] = None