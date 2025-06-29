from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Base schema for shared fields
class GetintouchtBase(BaseModel):
    name: str
    email: EmailStr
    message: str

# Schema used when creating a contact submission
class GetintouchCreate(GetintouchtBase):
    pass

# Schema used when returning a contact submission
class GetintouchOut(GetintouchtBase):
    id: int
    created_at: datetime  # ✅ CORRECT

    class Config:
        orm_mode = True
