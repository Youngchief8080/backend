from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time

class BookingItemBase(BaseModel):
    sub_service_id: int
    name: str
    price: float
    quantity: int

    class Config:
        orm_mode = True

class BookingCreate(BaseModel):
    user_id: str
    contact_info: str
    date: date
    time: time
    total_amount: float
    notes: Optional[str] = None
    points_used: Optional[int] = 0  # 👈 Add this
    status: Optional[str] = None
    items: List[BookingItemBase]

class BookingItemResponse(BaseModel):
    id: int
    sub_service_id: int
    name: str
    price: float
    quantity: int

    class Config:
        orm_mode = True

class BookingResponse(BaseModel):
    id: int
    user_id: str
    contact_info: str
    date: date
    time: time
    total_amount: float
    status: str
    notes: Optional[str] = None
    items: List[BookingItemResponse] = []

    class Config:
        orm_mode = True

class BookingUpdate(BaseModel):
    status: Optional[str] = None
    contact_info: Optional[str] = None
    notes: Optional[str] = None