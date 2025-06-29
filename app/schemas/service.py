from pydantic import BaseModel
from typing import Optional, List


# Base Service schema
class ServiceBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None


# Create schema
class ServiceCreate(ServiceBase):
    pass  # image_url can be handled separately if needed


# Update schema
class ServiceUpdate(ServiceBase):
    pass


# Sub-service output schema
class SubServiceOut(BaseModel):
    id: int
    name: str
    description: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


# Final service output schema
class ServiceOut(ServiceBase):
    id: int
    image_url: Optional[str] = None
    sub_services: List[SubServiceOut] = []  # List of sub-service objects

    class Config:
        orm_mode = True
