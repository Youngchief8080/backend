

from pydantic import BaseModel
from typing import Optional


class TeamsBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamsCreate(TeamsBase):
    pass  # No image_url here


class TeamsUpdate(TeamsBase):
    pass  # No image_url here


class TeamsOut(TeamsBase):
    id: int
    image_url: Optional[str] = None  # Only here for response

    class Config:
        orm_mode = True
