

from pydantic import BaseModel
from typing import Optional


class PasteventBase(BaseModel):
    name: str
    description: Optional[str] = None


class PasteventCreate(PasteventBase):
    pass  # No image_url here


class PastevetUpdate(PasteventBase):
    pass  # No image_url here


class PasteventOut(PasteventBase):
    id: int
    image_url: Optional[str] = None  # Only here for response

    class Config:
        orm_mode = True
