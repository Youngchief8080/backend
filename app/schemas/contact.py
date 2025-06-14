# app/schemas/contact.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ContactForm(BaseModel):
    subject: str
    message: str
    status: str = 'pending'  # Match DB default
    user_id:int
    user_name: Optional[str] = None

class ContactResponse(BaseModel):
    id: int
    subject: str
    message: str
    status: str = 'pending'  # Consistent with DB model
    user_id: int # Make consistent with Form
    user_name: Optional[str] = None  # Make consistent with Form
    created_at: datetime

    class Config:
        orm_mode = True