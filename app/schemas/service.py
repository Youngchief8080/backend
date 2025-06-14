from pydantic import BaseModel
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass  # No image_url here


class ServiceUpdate(ServiceBase):
    pass  # No image_url here


class ServiceOut(ServiceBase):
    id: int
    image_url: Optional[str] = None  # Only here for response

    class Config:
        orm_mode = True
