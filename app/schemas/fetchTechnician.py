
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional


class TechnicianMinimalOut(BaseModel):
    id: int
    full_name: Optional[str] = None

    class Config:
        orm_mode = True