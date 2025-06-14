
# schemas/gallery.py
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class GalleryBase(BaseModel):
    title: str
    description: str
    category: str
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None

class GalleryCreate(GalleryBase):
    pass

class GalleryUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None

class GalleryInDBBase(GalleryBase):
    id: int

    class Config:
        orm_mode = True

# Additional schemas can be added here if needed
class Gallery(GalleryInDBBase):
    pass

class GalleryInDB(GalleryInDBBase):
    pass