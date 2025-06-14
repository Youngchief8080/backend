from pydantic import BaseModel
from typing import Optional

class SubServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None  # Optional for uploads
    service_id: int

    class Config:
        orm_mode = True


class SubServiceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    service_id: int

    class Config:
        orm_mode = True


class SubServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class SubServiceOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None  # <-- Make this Optional too

    class Config:
        orm_mode = True
