
# app/schemas/news.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    description: str
    category: str
    content: str
    image_url: Optional[str] = None

class NewsCreate(NewsBase):
    pass

class NewsUpdate(NewsBase):
    pass

class NewsOut(NewsBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
